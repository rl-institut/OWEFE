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

# Digester operation parameters
# temperature inside of the digester = 35 degree Celsius (source: final year project, 2021, Beirut Arab University)
retention_time = 22
# Characteristic of input sludge
# incoming organic matter flow
design_mass_flowrate = inpdf["wastewater"].max()  # [kg/
sludge_density = 997  # kg/m3 (source: final year project, 2021, Beirut Arab University)
sludge_specific_gravity = 1.02  # unitless, (source: final year project, 2021, Beirut Arab University)
heat_capacity_sludge = 4200  # J/kg°C heat capacity dewatered sludge assumed to be same as water
# (source: final year project, 2021, Beirut Arab University)
yield_factor = 9.3  # (source: final year project, 2021, Beirut Arab University)
# dry solid concentration = 20% of wet feedstock sludge (source: final year project, 2021, Beirut Arab University)
# volatile solid concentration = 80% of dry solid (source: final year project, 2021, Beirut Arab University)

print(design_mass_flowrate)

digester_design = Digester(retention_time, design_mass_flowrate, sludge_density, sludge_specific_gravity, yield_factor)
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
