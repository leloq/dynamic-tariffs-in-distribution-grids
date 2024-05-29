from copy import deepcopy
import os
import pandas as pd
import random
import traceback
import numpy as np

import edisgo
from edisgo.edisgo import import_edisgo_from_files
from edisgo.network.results import Results
from edisgo.flex_opt import check_tech_constraints


debug = True
grid_dir = r"input/grids"
res_dir = r"output"
file_name_constant = \
    "00_pricing_constant_operation_dynamic_fi_fit_ne_volumetric_gridch_False_HPnew.pkl"
files_name_dynamic = \
    [file for file in os.listdir(res_dir) if file.endswith("HPnew.pkl") and
     (file != file_name_constant)]
check_existence = True


def get_grid_issues(edisgo_obj):
    voltage_diff = check_tech_constraints.voltage_deviation_from_allowed_voltage_limits(
        edisgo_obj
    )

    # Get score for nodes that are over or under the allowed deviations
    voltage_diff = voltage_diff[voltage_diff != 0.0]
    # drop components and time steps without violations
    voltage_diff = voltage_diff.dropna(how="all").dropna(how="all", axis=1).fillna(0)
    # Get current relative to allowed current
    relative_i_res = check_tech_constraints.components_relative_load(edisgo_obj)

    # Get lines that have violations
    crit_lines_score = relative_i_res[relative_i_res > 1]
    # drop components and time steps without violations
    crit_lines_score = (
        crit_lines_score.dropna(how="all").dropna(how="all", axis=1).fillna(0)
    )
    return voltage_diff, crit_lines_score


def adapt_time_series(
        edisgo_object: edisgo.EDisGo,
        timeseries_constant: pd.DataFrame,
        timeseries_dynamic: pd.DataFrame,
        share_dynamic: float):
    """
    Updates time series of relevant loads in edisgo_obj to new data with dynamic and
    constant tariff. ´share_dyn´ thereby determines the share of households that follow
    the dynamic tariff. Note: The columns of ts_constant and ts_dynamic have to be valid
    load names in edisgo_obj in order to properly function.

    :param edisgo_object: grid container object
    :param timeseries_constant:
        time series of residential loads following a constant tariff
    :param timeseries_dynamic:
        time series of residential loads following a dynamic tariff
    :param share_dynamic: share of loads that follows the dynamic tariff. Has to lie
        between 0 and 1
    :return:
    """
    nr_loads_dynamic = int(len(timeseries_constant.columns) * share_dynamic)
    timeseries_new = pd.concat([timeseries_constant.iloc[:, nr_loads_dynamic:],
                        timeseries_dynamic.iloc[:, :nr_loads_dynamic]], axis=1)
    loads_active_power_new = edisgo_object.timeseries.loads_active_power.copy()
    loads_active_power_new.update(timeseries_new)
    edisgo_object.timeseries.loads_active_power = loads_active_power_new
    return edisgo_object


grids = os.listdir(grid_dir)
orig_seed = 2022
random.seed(orig_seed)
# define load and feed-in days
ts_dict = {
    "feed-in": pd.date_range(start="2011-04-10", periods=24, freq="1h").append(
                    pd.date_range(start="2011-04-22", periods=24, freq="1h")),
    "load": pd.date_range(start="2011-12-08", periods=24, freq="1h").append(
                    pd.date_range(start="2011-12-12", periods=24, freq="1h")).append(
                    pd.date_range(start="2011-12-01", periods=24, freq="1h")).append(
                    pd.date_range(start="2011-01-26", periods=24, freq="1h")),
    "debug": pd.date_range(start="2011-04-10", periods=24, freq="1h").append(
                    pd.date_range(start="2011-12-08", periods=24, freq="1h")).append(
                    pd.date_range(start="2011-12-12", periods=24, freq="1h")).append(
                    pd.date_range(start="2011-12-01", periods=24, freq="1h")).append(
                    pd.date_range(start="2011-04-22", periods=24, freq="1h")).append(
                    pd.date_range(start="2011-01-26", periods=24, freq="1h")),
    "full": pd.date_range(start="2011-01-01", periods=8760, freq="1h")
}

ts_constant_orig = \
    pd.read_pickle(os.path.join(res_dir, file_name_constant)).divide(1000)

for grid_id in grids:
    try:
        int(grid_id)
    except ValueError:
        continue
    # try:
    if os.path.isdir(r"output\grid_reinforcement_results\{}\base\topology".format(grid_id)):
        edisgo_obj = import_edisgo_from_files(
            r"output\grid_reinforcement_results\{}\base".format(grid_id), import_timeseries=True)
    else:
        # import grid
        grid_dir_tmp = f"{grid_dir}/{grid_id}/grid_data_eGon2021.zip"

        edisgo_obj = import_edisgo_from_files(grid_dir_tmp, import_timeseries=True)

        # set time series for conventional generators, produce at full capacity
        conventional_gens = edisgo_obj.topology.generators_df.loc[
            ~edisgo_obj.topology.generators_df.index.isin(
                edisgo_obj.timeseries.generators_active_power.columns)
        ]
        conventional_gens_p = pd.DataFrame(index=edisgo_obj.timeseries.timeindex,
                                           columns=conventional_gens.index)
        conventional_gens_p[conventional_gens.index] = conventional_gens.p_nom
        edisgo_obj.set_time_series_manual(generators_p=conventional_gens_p)

        # set reactive powers
        edisgo_obj.set_time_series_reactive_power_control()

        # check resulting edisgo object
        edisgo_obj.check_integrity()
        edisgo_obj.reinforce(reduced_analysis=True, catch_convergence_problems=True)
        edisgo_obj.results.to_csv(
            f"{res_dir}/grid_reinforcement_results/{grid_id}/base",
            parameters={"grid_expansion_results": ["grid_expansion_costs",
                                                   "unresolved_issues"]})
        edisgo_obj.save(f"{res_dir}/grid_reinforcement_results/{grid_id}/base",
                        save_results=False)
        edisgo_obj.results = Results(edisgo_obj)
    edisgo_orig = deepcopy(edisgo_obj)

    # extract residential loads
    residential_loads = edisgo_obj.topology.loads_df.loc[
        edisgo_obj.topology.loads_df.sector == "residential"
    ]
    nr_residential_loads = len(residential_loads)

    # add new time series
    loads_index = np.random.randint(0, len(ts_constant_orig.columns), nr_residential_loads)
    ts_constant = ts_constant_orig.iloc[:, loads_index]
    ts_constant.index = edisgo_obj.timeseries.timeindex
    ts_constant.columns = range(nr_residential_loads)
    for file_name_dynamic in files_name_dynamic:
        edisgo_obj = deepcopy(edisgo_orig)
        ts_dynamic_orig = \
            pd.read_pickle(os.path.join(res_dir, file_name_dynamic)).divide(1000)
        ts_dynamic = ts_dynamic_orig.iloc[:, loads_index]
        ts_dynamic.index = edisgo_obj.timeseries.timeindex
        ts_dynamic.columns = range(nr_residential_loads)
        # vary share of dynamically controlled loads
        for share_dyn in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for mode in ["feed-in", "load", "debug"]:
                try:
                    res_dir_tmp = os.path.join(res_dir, "grid_reinforcement_results", str(grid_id),
                                               file_name_dynamic, str(share_dyn), mode)
                    if check_existence:
                        if os.path.isdir(f"{res_dir_tmp}/grid_expansion_results"):
                            print(f"{grid_id}-{mode} for tariff {file_name_dynamic}-{share_dyn} already solved. Skipping.")
                            continue
                    edisgo_obj = deepcopy(edisgo_orig)
                    edisgo_obj.timeseries.timeindex = ts_dict[mode]
                    nr_loads_dyn = int(nr_residential_loads * share_dyn)
                    seeds = random.sample(range(0, nr_residential_loads), nr_loads_dyn)
                    loads_dyn = ts_constant.iloc[:, seeds].columns
                    loads_constant = \
                        ts_constant.columns[~ts_constant.columns.isin(loads_dyn)]
                    ts_new = pd.concat([ts_constant[loads_constant],
                                        ts_dynamic[loads_dyn]], axis=1)
                    ts_new.columns = residential_loads.index
                    ts_loads_active_power_new = \
                        edisgo_obj.timeseries.loads_active_power.copy()
                    ts_loads_active_power_new.update(ts_new)
                    edisgo_obj.timeseries.loads_active_power = ts_loads_active_power_new
                    edisgo_obj.analyze()
                    voltage_diff, crit_lines_score = get_grid_issues(edisgo_obj)
                    os.makedirs(f"{res_dir_tmp}/results_before_reinforcement", exist_ok=True)
                    voltage_diff.to_csv(f"{res_dir_tmp}/results_before_reinforcement/voltage_diff.csv")
                    crit_lines_score.to_csv(f"{res_dir_tmp}/results_before_reinforcement/overloading.csv")
                    edisgo_obj.reinforce(reduced_analysis=True, catch_convergence_problems=True)
                    edisgo_obj.analyze()
                    edisgo_obj.results.to_csv(f"{res_dir_tmp}")
                except Exception:
                    print(f"Something went wrong with grid {grid_id}-{mode} for tariff {file_name_dynamic}-{share_dyn}.")
                    traceback.print_exc()
print("Success")
