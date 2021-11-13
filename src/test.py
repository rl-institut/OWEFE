from digester_demand import HeatCalculation

heat_mapping = HeatCalculation(temp_ambient=1, heat_transfer_coefficient=1, temp_digester=35,
                               surface_area=10, heat_capacity=2000, om_flow=55)

heat_demand_digester = heat_mapping.compute()
print(heat_demand_digester)
