from constructedwetlands import Constructed_wetlands
parameter = Constructed_wetlands(308.1, 277.29)
avg_discharge, cw_area, net_evaporation, BOD_effluent, COD_effluent, NO3_effluent, K1, cw_area, a_1, a_2, a_3, net_evaporation = parameter.compute()
print('BOD5 effluent : ', round(BOD_effluent, 2))
print('COD effluent : ', round(COD_effluent, 2))
print('Nitrate effluent: ', round(NO3_effluent, 2))
print(K1)
print(cw_area)
print(a_1, a_2, a_3, net_evaporation)