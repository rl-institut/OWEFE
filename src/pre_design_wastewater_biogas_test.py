# digester file located in src >>> components
# Proceeded csv file will be auto generated in the same directory

import pandas as pd
import os

from components.digester import Digester
from digester_demand import HeatCalculation
from digester_demand import ElectricityCalculation

os.chdir("../examples/")
inpdf = pd.read_csv(r'ww_biogas_tibnine_raw.csv')
# incoming organic matter flow
design_flow = inpdf["wastewater"].mean()
# heat capacity of organic matter flow in this case: dewatered sludge assumed to be same as water Cp = 4200 J/kg °C;
# Source: El Joauhari et al. 2021
heat_capacity_sludge = 4200
print(design_flow)

retention_time = 22
digester_design = Digester(retention_time, design_flow)
diameter, volume, bg_prod, surface_area_total = digester_design.compute()
print('surface_area_total: ', round(surface_area_total, 2))

for i, r in inpdf.iterrows():
    heat_demand = HeatCalculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                  temp_digester=35, surface_area=surface_area_total,
                                  heat_capacity=heat_capacity_sludge, om_flow=design_flow)
    inpdf.loc[i, "heat_demand_digester"] = heat_demand.compute()

inpdf.to_csv("ww_biogas_tibnine_proceed_test.csv", index=False)

for i, r in inpdf.iterrows():
    electricity_demand = ElectricityCalculation(wastewater=r['wastewater'])
    inpdf.loc[i, "electricity_demand_digester"] = electricity_demand.compute()

inpdf.to_csv("proceeded csv file", index=False)
