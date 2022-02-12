# Assumptions
# 1) optimum dimension rate: diameter : total_height = 1.5 : 1;
# (Source: michigan.gov/documents/deq/wrd-ot-anaerobic-digestion-process, 2013))

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

     ******** weight of dry and volatile solids *******
     (Source: michigan.gov/documents/deq/wrd-ot-anaerobic-digestion-process, 2013))

     weight of dry solids [kg/h]= weight of wet feedstock sludge * dry solid concentration(%)

     weight of volatile solids [Kg/h] = weight of dry solids * Volatile solid concentration(%)

     ******** calculation of feedstock to biogas conversion factor********


    Bio-gas production [m3 /h] = {Yield factor * volume of digester [m3] * initial concentration of volatile solids} / 1000
    (Source: Irena 2016)
     where,
           kg to be equal to litre, final value is divided by 1000 to convert from litres to m3
           Yield factor based on temperature and retention time (Source: IRENA_statistics_Measuring_scale_biogas/table7, 2016)
           volume of digester [m³] = volume of cone + volume of cylinder
           initial concentration of volatile solids [kg/m³] = weight of volatile solids [kg/h] / volumetric_flow [m3/h]
           volatile solids flow rate = dewatered sludge mass flow rate (input-to-model) * 0.2 * 0.8

"""

import math
import numpy as np


class Digester:
    def __init__(self, retention_time, design_mass_flow, sludge_density, sludge_specific_gravity, yield_factor):
        self.retention_time = retention_time
        self.design_mass_flow = design_mass_flow
        self.sludge_density = sludge_density
        self.sludge_specific_gravity = sludge_specific_gravity
        self.yield_factor = yield_factor
        if self.retention_time > 30:  # retention_time in days
            self.yield_factor = 10.59

        # Unit: [m³/days] Multiply by 24 to convert hour to days

    def compute(self):
        volumetric_flow = self.design_mass_flow * 24 / (self.sludge_density * self.sludge_specific_gravity)
        filled_up_volume = volumetric_flow * self.retention_time  # filled up volume is constant
        # assuming that there is continuous & constant input of dewatered sludge (retention time to hours)
        height3 = np.cbrt(filled_up_volume / (math.pi * (3.06 / 2) ** 2))
        # diameter-height3 ratio = 3.06 (calculated above)
        height2 = height3 / 0.7
        height1 = 3 / 7 * height2
        total_height_digester = height1 + height2
        diameter = 1.5 * total_height_digester
        radius = diameter / 2
        volume_total = (math.pi * radius ** 2 * height2) + (1 / 3 * math.pi * radius ** 2 * height1)
        surface_area_cone = math.pi * radius * (radius + math.sqrt(height1 ** 2 + radius ** 2))
        surface_area_cylinder_overground = 2 * math.pi * radius * height2
        floor_area = math.pi * radius ** 2
        surface_area_total = surface_area_cylinder_overground + surface_area_cone + floor_area
        total_dry_solids = 0.2 * self.design_mass_flow  # [kg/h]
        total_vs_loading = 0.8 * total_dry_solids  # [kg/h], total volatile solid loading
        olr = total_vs_loading / filled_up_volume * 24  # [kg vs/m³.d], organic loading rate
        conversion_factor = (volume_total * self.yield_factor * 0.2 * 0.8) / 1000  # [m³/h] formula explained above
        return diameter, volume_total,conversion_factor, surface_area_total, filled_up_volume, olr, volumetric_flow
