# Dynamic Tariffs in Distribution Grids

🚀 **Overview**

This repository provides an open-source framework to analyze the impact of dynamic tariffs and regulatory options on distribution grid reinforcement costs. It includes tools to simulate the operation of household home energy management systems, create load profiles under constant and dynamic tariff adoption, calculate grid reinforcement costs based on PyPSA power flow simulations and the eDisGO package, and visualize results.

📄 **Key Features:**
1. **Household Simulations**: Create household load profiles, based on different regulatory scenarios (e.g., dynamic tariff adoption, grid charge design, feed-in temuneration)
2. **Grid Reinforcement Analysis**: Assess costs for grid upgrades required due to different tariff schemes.
3. **Visualization Tools**: Generate insights from simulation results.

## 🧩 Key Steps

1. **Prepare Target Dataset**:
   - Use `00 Preprocessing_EV_data.ipynb` and `00 Set Up Cases.ipynb` to generate input data.

2. **Simulate Household Profiles**:
   - Run `01 Create Dynamic and Constant Profiles.ipynb` to simulate profiles under various scenarios.

3. **Calculate Grid Reinforcement Costs**:
   - Use `04_Calculate_Reinforcement_Costs.py` to compute costs for grid upgrades.


---

## 📚 Cited Sources

### Heat Pump and Household Load Profiles:
- Schlemminger, M., Ohrdes, T., Schneider, E., & Knoop, M. (2022). Dataset on electrical single-family house and heat pump load profiles in Germany. *Scientific Data, 9*(1), 56.

### Electric Vehicle Charging Data:
- Sørensen, Å. L., Lindberg, K. B., Sartori, I., & Andresen, I. (2021). Residential electric vehicle charging datasets from apartment buildings. *Data in Brief, 36*, 107105.
- Sørensen, Å. L., Lindberg, K. B., Sartori, I., & Andresen, I. (2021). Analysis of residential EV energy flexibility potential based on real-world charging reports and smart meter data. *Energy and Buildings, 241*, 110923.

### PV Generation:
- Pfenninger, S. & Staffell, I. (2016). Long-term patterns of European PV output using 30 years of validated hourly reanalysis and satellite data. *Energy, 114*, 1251-1265. doi: 10.1016/j.energy.2016.08.060
- Staffell, I. & Pfenninger, S. (2016). Using Bias-Corrected Reanalysis to Simulate Current and Future Wind Power Output. *Energy, 114*, 1224-1239. doi: 10.1016/j.energy.2016.08.068
  - *(realized with renewables.ninja)*

### BESS Sizing:
- Semmelmann, L., Konermann, M., Dietze, D., & Staudt, P. (2024). Empirical field evaluation of self-consumption promoting regulation of household battery energy storage systems. *Energy Policy, 194*, 114343.

---


## 📂 Repository Structure

### **Input and Output**
- **`input/`**: Contains data that is later used
- - **`input/preprocessed`**: Contains characteristics and time series of the 500 modelled households
- **`output/`**: Stores results from simulations. We note that we have removed most of the output files to reduce the size of the repository. We can provide the resulting files upon request.

### **Notebooks and Scripts**
1. **`00 Preprocessing_EV_data.ipynb`**:
   - Prepares EV charging data for household simulations.

2. **`00 Set Up Cases.ipynb`**:
   - Generates and explains the target dataset used in the simulations.

3. **`01 Create Dynamic and Constant Profiles.ipynb`**:
   - Simulates household behavior based on dynamic or constant tariffs and regulatory options.
   - In the following part, different scenarios can be adopted: 

     ```python
        debug = False # -> determines if results are saved in output folder
        household_n = 500 # number of simulated households must be less than 500
        
        for pricing_type in ["dynamic"]: # decides if all households in the sample follow constant or dynamic tariffs ["constant","dynamic"]
            for grid_charge_type in ["volumetric"]: # determines the grid charge design, can be: ["volumetric","peak","segmented","rotating"]:
                for feed_in_type in ["fit"]: # determines the way PV feed in is remunerated ["fit","dynamic"]
                    for grid_charging_allowed in [False]: # determines if households can charge their BESS from the grid, default is False
        
                        # "dynamic" or "constant"
                        operation_type = "dynamic"  # determines if household's home energy management systems are operated dynamically, can either be "dynamic" or "constant"
                        ev_charging_strategy = "early"  # "early" or "spread"; only relevant for operation_type = "constant"
     ```

4. **`02 Analyze Aggregated Household Profiles and Regulatory Cases.ipynb`**:
   - Aggregates results and evaluates regulatory scenarios from a peak load perspective
  

5. **`03 Calculate_Reinforcement_Costs.py`**:
   - Distribute the modelled household loads over ding0 grid topologies, run PyPSA power flow analysis and calculate reinforcement costs with eDisGO

6. **`04 Visualize Profiles.ipynb`**:
   - Visualize resulting load profiles under different regulatory scenarios


### **Other Files**
- **`requirements.txt`**: Contains the Python dependencies required to run the project.

---





## 💻 Requirements

To install the dependencies, run:
```bash
pip install -r requirements.txt
```
The code has been tested with Python 3.8.8.

---

## Changelog

25.04.2025: Clean version: Cleaning up file structure, improving structure of household calculations, adding documentation, fixing minor bug in BESS efficiency calculations due to double consideration (note: we checked the influence of the bug on the peak load calculations, which were minimal and did not change the direction of the results), deleting unnecessary files, removed files from output folder to reduce size of repository

07.10.2024: Official release for calculations in the underlying paper

---

## 🌟 Contributors
Leo Semmelmann, Katharina Kaiser, Anya Heider
