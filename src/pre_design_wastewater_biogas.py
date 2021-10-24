# digester file located in src >>> components
# Proceeded csv file will be auto generated in the same location or directory

import pandas as pd
# import os
# os.chdir("../src/")
from components.digester import Digester
from digester_demand import heat_calculation
from digester_demand import electricity_calculation

inpdf = pd.read_csv(r'Your csv file')
flow = inpdf["wastewater"].mean()
print(flow)

retention_time = 22
surface_area = Digester(retention_time, flow)
diameter, volume, bg_prod, area = surface_area.compute()
print('surface_area_total_overground: ', round(area, 2))

for i, r in inpdf.iterrows():
    heat_demand = heat_calculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                   temp_digester=35, surface_area_total_overground= area)
    inpdf.loc[i, "heat_demand_digester"] = heat_demand.compute()

inpdf.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

for i, r in inpdf.iterrows():
    electricity_demand = electricity_calculation(wastewater=r['wastewater'])
    inpdf.loc[i, "electricity_demand_digester"] = electricity_demand.compute()

inpdf.to_csv("proceeded csv file ", index=False)
