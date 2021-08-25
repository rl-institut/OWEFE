import math
import pandas as pd
# col_list = ["timestep", "demand_el", "demand_th", "demand_water", "demand_f", "wastewater"]
data = pd.read_csv(r"basic_example_copy.csv", usecols=["timestep", "demand_el", "demand_th", "demand_water", "demand_f", "wastewater"])
design_flow= data["wastewater"].mean()
# print(data,f'wasterwater mean: {degine_flow}')



class Digester:
    def __init__(self, height, retention_time):
        self.height = height
        self.retention_time = retention_time

    def compute(self, yield_factor=8.26): # temperature is remain in a range of 31 - 33 degree Celsius
        height1 = 0.3 * self.height  # height for gas storage
        height2 = 0.7 * self.height  # height for digester volume
        volume = design_flow * self.retention_time * 24 # retention time is in days so changing in hours
        radius = math.sqrt(volume / ((math.pi * height1 / 3) + (math.pi * height2)))
        diameter = 2 * radius
        vol_solid_load = 1.6 # KgVSS/day/m3; for retention time 30 - 40 days is low rate digestion range: 0.6 - 1.6
        initial_conc_volatile = ((vol_solid_load /24) / design_flow) # Divide by 24 to change day into hour as design flow in m3/hour
        if self.retention_time > 36: #retention_time in days
            yield_factor = 7.44
        conv_factor = (volume * yield_factor * initial_conc_volatile) / 1000
        return diameter, volume, conv_factor
