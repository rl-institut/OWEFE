# we assume an
# 1) optimum dimension rate: diameter : height = 2 : 1;
# 2) height of conical top (height1) = 0.3 * height;
# 3) height of cylinder (height2) = 0.7 * height; maximum filling level (height3) = 0.7 * height2;
# pls check literature on crazy assumptions

import math
import numpy as np


class Digester:
    def __init__(self, retention_time, design_flow):
        self.retention_time = retention_time
        self.design_flow = design_flow

    def compute(self, yield_factor=8.26):  # temperature is remain in a range of 31 - 33 degree Celsius

        filled_up_volume = self.design_flow * self.retention_time * 24  # retention time is in days so changing in hours

        height3 = np.cbrt(filled_up_volume / (math.pi * (4.08 / 2) ** 2))
        height2 = height3 / 0.7
        height1 = 3 / 7 * height2
        height = height1 + height2
        radius = height
        diameter = 2 * radius
        volume_total = math.pi * radius ** 2 * height2 + 1 / 3 * math.pi * radius ** 2 * height1
        surface_area_cone = math.pi * radius*(radius + math.sqrt(height1**2+radius**2))
        surface_area_cylinder_overground = 2*math.pi * radius + height2
        surface_area_total_overground = surface_area_cylinder_overground + surface_area_cone
        vol_solid_load = 1.6  # KgVSS/day/m3; for retention time 30 - 40 days is low rate digestion range: 0.6 - 1.6
        initial_conc_volatile = ((vol_solid_load / 24) / self.design_flow)  # Divide by 24 to change day into hour as design flow in m3/hour
        if self.retention_time > 36:  # retention_time in days
            yield_factor = 7.44
        conv_factor = (volume_total * yield_factor * initial_conc_volatile) / 1000
        return diameter, volume_total, conv_factor, surface_area_total_overground
