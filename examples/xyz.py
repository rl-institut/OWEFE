import os
os.chdir("../src/")
from src.components.digester import Digester

os.chdir("../examples/components/")
from components.constructedwetlands import Constructed_wetlands

#from components.digester import Digester
#from components.constructedwetlands import Constructed_wetlands

retention_time = 22
bg_prod = Digester(retention_time =22, design_flow = 0.985)
design_diameter, volume, bg_prod_result, surface_area_total_overground = bg_prod.compute()
print(f'Total design diameter : {round(design_diameter, 2)} meter')
print(f'Total volume of digester : {round(volume, 2)} m3')
print('biogas conversion factor: ', round(bg_prod_result, 2))

parameter = Constructed_wetlands(130, 115)
avg_discharge, cw_area, net_evaporation, BOD_effluent, COD_effluent, NO3_effluent = parameter.compute()
print('BOD5 effluent : ', round(BOD_effluent, 2))
print('COD effluent : ', round(COD_effluent, 2))
print('Nitrate effluent: ', round(NO3_effluent, 2))
