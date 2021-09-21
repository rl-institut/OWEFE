import pandas as pd

from digester_demand import heat_calculation
from digester_demand import electricity_calculation
from digester import Digester

inpdf = pd.read_csv(r'temperature1.csv')
outdf = pd.read_csv(r'basic_example_copy_1.csv')
flow = outdf["wastewater"].mean()
print(flow)

surface_area = Digester(22, flow)
diameter, volume, bg_prod, area = surface_area.compute()
print('surface_area_total_overground: ', round(area, 2))

for i, r in inpdf.iterrows():
    heat_demand = heat_calculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                   temp_digester=35, surface_area_total_overground= area)
    outdf.loc[i, "heat_demand_digester"] = heat_demand.compute()

outdf.to_csv("test_file.csv", index=False)

for i, r in outdf.iterrows():
    electricity_demand = electricity_calculation(wastewater=r['wastewater'])
    outdf.loc[i, "electricity_demand_digester"] = electricity_demand.compute()

outdf.to_csv("test_file.csv", index=False)
