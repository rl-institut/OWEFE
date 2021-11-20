import pandas as pd
import os
os.chdir("../src/")
from digester_demand import HeatCalculation
from digester_demand import ElectricityCalculation
from components.digester import Digester
os.chdir("../examples/")

inpdf = pd.read_csv(r'ww_biogas_tibnine_raw.csv')
# Units of raw data file: wastewater/dewatered_sludge [kg/h], heat demand [kWh/h],
# electricity demand [kWh/h], water demand [m³]

# incoming organic matter flow
design_mass_flowrate = inpdf["wastewater"].max()  # [kg/h]

# heat capacity of organic matter flow in this case: dewatered sludge assumed to be same as water Cp = 4200 J/kg °C;
# Source: El Joauhari et al. 2021
heat_capacity_sludge = 4200
print(design_mass_flowrate)

retention_time = 22
digester_design = Digester(retention_time, design_mass_flowrate)
diameter, volume, bg_prod, surface_area_total, filled_up_volume, organic_loading_rate, volumetric_flowrate = digester_design.compute()
print('surface_area_total: ', round(surface_area_total, 2))

for i, r in inpdf.iterrows():
    heat_demand = HeatCalculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                  temp_digester=35, surface_area=surface_area_total,
                                  heat_capacity=heat_capacity_sludge, om_flow=design_mass_flowrate)
    inpdf.loc[i, "heat_demand_digester"] = heat_demand.compute()

inpdf.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

for i, r in inpdf.iterrows():
    electricity_demand = ElectricityCalculation(om_flow=r['wastewater'], filled_up_volume=filled_up_volume)
    inpdf.loc[i, "electricity_demand_digester"] = electricity_demand.compute()

inpdf.to_csv("ww_biogas_tibnine_proceed.csv", index=False)
