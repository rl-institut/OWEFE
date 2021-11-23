# Assumptions
# 1) optimum dimension rate: diameter : total_height = 1.5 : 1;
# (Source: michigan.gov/documents/deq/wrd-ot-anaerobic-digestion-process, 2013))
# 2) density of sludge = 997 kg/m3 (source: final year project, 2021, Beirut Arab University)
# 3) specific gravity of sludge = 1.02 (source: final year project, 2021, Beirut Arab University)
# 4) temperature inside of the digester = 35 degree Celsius (source: final year project, 2021, Beirut Arab University)
# 5) solid concentration = 20% of wet feedstock sludge (source: final year project, 2021, Beirut Arab University)
# 6) volatile solid concentration = 80% of dry solid (source: final year project, 2021, Beirut Arab University)
"""
    ********** Dimension of Digester ************
    digester type: floating drum plant (photo source: IRENA_statistics_Measuring_scale_biogas, 2016)
    height of conical top (height1) = 0.3 * total_height;
    height of cylinder (height2) = 0.7 * total_height; maximum filling level (height3) = 0.7 * height2;

    ****** Relation between diameter and height3*******
     Total height of (h) = height1 + height2
          h = 0.3h + 0.7h
     so,
            height2 = 0.7h
     height3 = 0.7 * height2 # height3 is the maximum filling level for the sludge
     height3 = 0.7 * 0.7 h
     height3 = 0.49 h

     Here, we suppose diameter : height = 1.5 : 1

     diameter = 1.5 * height
              = 1.5 * (height3 / 0.49)
              = 3.06 height3

     ******** calculation of height3****
     filled up volume = math.pi * (diameter/2) ** 2 * height 3

     ******** weight of dry and volatile solids ******* (source: (Source: michigan.gov/documents/deq/wrd-ot-anaerobic-digestion-process, 2013))
     Wt.of dry solids (Kg/hour)= Wt.of wet feedstock sludge * solid concentration(%)

     Wt.of volatile solids (Kg/hour) = Wt.of dry solid * Volatile solid concentration(%)

     ******** calculation of bio-gas production********
     Bio-gas production (m3 /hour) = [Yield factor * volume of digester (m3) * initial concentration of volatile solids (kg/m3)] / 1000
     where,
           kg to be equal to litre, final value is divided by 1000 to convert from litres to m3
           Yield factor based on temperature and retention time (Source: IRENA_statistics_Measuring_scale_biogas/table7, 2016)
           volume of digester = volume of cone + volume of cylinder
           initial concentration of volatile solids = Wt.of volatile solids (Kg/hour) / volumetric_flowrate (m3/hour)
           wt. of volatile solids = Mass flow rate [input-to-model] * 0.2 * 0.8

"""

import math
import numpy as np


class Digester:
    def __init__(self, retention_time, design_mass_flowrate, sludge_density, sludge_specific_gravity, yield_factor):
        self.retention_time = retention_time
        self.design_mass_flowrate = design_mass_flowrate
        self.sludge_density = sludge_density
        self.sludge_specific_gravity = sludge_specific_gravity
        self.yield_factor = yield_factor
        self.volumetric_flowrate = self.design_mass_flowrate * 24 / (self.sludge_density * self.sludge_specific_gravity)
        # Unit: [m³/days] Multiply by 24 to convert hour to days
    def compute(self):
        volumetric_flowrate = self.design_mass_flowrate * 24 / (self.sludge_density * self.sludge_specific_gravity)

        filled_up_volume = volumetric_flowrate * self.retention_time   # filled up colume is constant
        # assuming that there is continuous & constant input of dewatered sludge (retention time to hours)
        height3 = np.cbrt(filled_up_volume / (math.pi * (3.06 / 2) ** 2))  # value 3.06 is calculated above
        height2 = height3 / 0.7
        height1 = 3 / 7 * height2
        total_height_digester = height1 + height2
        diameter = 1.5 * total_height_digester
        radius = diameter / 2
        volume_total = (math.pi * radius ** 2 * height2) + (1 / 3 * math.pi * radius ** 2 * height1)
        surface_area_cone = math.pi * radius*(radius + math.sqrt(height1**2+radius**2))
        surface_area_cylinder_overground = 2*math.pi * radius * height2
        floor_area = math.pi * radius ** 2
        surface_area_total = surface_area_cylinder_overground + surface_area_cone + floor_area
        design_dry_solid_load = 0.2 * self.design_mass_flowrate
        design_volatile_load = 0.8 * design_dry_solid_load
        organic_loading_rate = design_volatile_load / filled_up_volume * 24 # Units hour to days
        if self.retention_time > 30:  # retention_time in days
            yield_factor = 10.59
        conv_factor = (volume_total * self.yield_factor * 0.2 * 0.8) / 1000  # unit conversion is described above
        return diameter, volume_total, conv_factor, surface_area_total, filled_up_volume, organic_loading_rate, volumetric_flowrate