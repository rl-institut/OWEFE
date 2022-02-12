# Floating Drum Plant Digester Model following the approach of biogas production calculation of El. Jouahari et al. 2021


"""
    ********** Dimension of Digester ************
    digester type: floating drum plant
    Optimum Design Suggestions:
    diameter : total_height = 1.5 : 1;
    (Source: michigan.gov/documents/deq/wrd-ot-anaerobic-digestion-process, 2013))
    height of conical top (height1) = 0.3 * total_height;
    height of cylinder (height2) = 0.7 * total_height; maximum filling level (height3) = 0.7 * height2;

    Relation between diameter and height3:
     Total height of (h) = height1 + height2
          h = 0.3h + 0.7h
     so,
            height2 = 0.7h
     height3 = 0.7 * height2 # height3 is the maximum filling level for the sludge
     height3 = 0.7 * 0.7 h
     height3 = 0.49 h

     diameter = 1.5 * height
              = 1.5 * (height3 / 0.49)
              = 3.06 height3

     ******** calculation of filled up volume****
     filled up volume = math.pi * (diameter/2) ** 2 * height 3

     ******** weight of dry and volatile solids *******
     (Source: michigan.gov/documents/deq/wrd-ot-anaerobic-digestion-process, 2013))
     weight of dry solids [kg/h]= weight of wet feedstock sludge * dry solid concentration(%)

     weight of volatile solids [Kg/h] = weight of dry solids * Volatile solid concentration(%)

     ******** calculation of feedstock to biogas conversion factor********

    biogas production [m³/h] = mf * sds * svs * rvsd * sgp
    where,
    mf = feedstock mass_flow [kg/h]
    sds = share of dry solids in feedstock
    svs =share of volatile solids in dry solid
    rvsd = volatile solid destruction rate
    sgp = specific gas production for destroyed volatile solids for chosen feedstock [m³/kg]
    (Source: Final Year Project, Beirut Arab University, 2021)
    feedstock to biogas conversion factor: f_b_cf = sds * svs * rvsd * sgp

"""

import math
import numpy as np


class Digester:
    def __init__(self, retention_time, design_mass_flow, volatile_solid_destruction_rate, sludge_density,
                 sludge_specific_gravity, dry_solid_concentration, volatile_solid_concentration,
                 specific_gas_production):
        self.retention_time = retention_time
        self.design_mass_flow = design_mass_flow
        self.volatile_solid_destruction_rate = volatile_solid_destruction_rate
        self.sludge_density = sludge_density
        self.sludge_specific_gravity = sludge_specific_gravity
        self.dry_solid_concentration = dry_solid_concentration
        self.volatile_solid_concentration = volatile_solid_concentration
        self.specific_gas_production = specific_gas_production

    def compute(self):
        volumetric_flow = self.design_mass_flow * 24 / (self.sludge_density * self.sludge_specific_gravity)
        filled_up_volume = volumetric_flow * self.retention_time  # assuming continuous & constant input of
        # filled up volume is constant

        # digester geometry
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

        # organic loading rate
        total_dry_solids = 0.2 * self.design_mass_flow  # [kg/h]
        total_vs_loading = 0.8 * total_dry_solids  # [kg/h], total volatile solid loading
        olr = total_vs_loading / filled_up_volume * 24  # [kg vs/m³.d], organic loading rate

        # feedstock to biogas conversion factor
        f_b_cf = self.dry_solid_concentration * self.volatile_solid_concentration\
                 * self.volatile_solid_destruction_rate * self.specific_gas_production  # formula explained above

        return diameter, volume_total, f_b_cf, surface_area_total, filled_up_volume, olr, volumetric_flow
