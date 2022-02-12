# Continuos Stirred Tank Reactor Digester Model following the approach for biogas production calculation of
# El Joauhari et al. (2021)

"""
    ********** Dimension of Digester ************
    Digester Type: Continuous Stirred Tank Reactor

   - open systems: material is free to enter or exit the system
   - operate on a steady-state basis: the conditions in the reactor don't change with time
   - reactants are continuously introduced into the reactor while products are continuously removed
   - well mixed -> uniform properties
   Source: University of Michigan, available online:
    https://encyclopedia.che.engin.umich.edu/Pages/Reactors/CSTR/CSTR.html

    Geometry
    Cylinder with rounded top including gas outlet and conic bottom for digested sludge outlet
    inflowing dewatered sludge fills cylindric middle part;
    for simplfication we assume a perfect cylinder for geometry calculations
    Digester Volume = π*r^2*h
    (Area which can be filled by inflowing dewatered sludge without space for gas and digested sludge)
    Surface Area = 2πr*(h+r)
    (Just Surface Area of cylinder)
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
        volume_total = volumetric_flow * self.retention_time
        radius = (volume_total/math.pi * 2/3)**(1/3)  # assuming a fixed height:radius ration of 3:2,
        # rearranged cylindric volume formula; h = 3/2 r
        diameter = 2*radius
        height = 3/2*radius
        surface_area_cylinder = 2 * math.pi * (radius + height)
        surface_area_total = surface_area_cylinder

        # organic loading rate
        total_dry_solids = 0.2 * self.design_mass_flow  # [kg/h]
        total_vs_loading = 0.8 * total_dry_solids  # [kg/h], total volatile solid loading
        olr = total_vs_loading / filled_up_volume * 24  # [kg vs/m³.d], organic loading rate

        # feedstock to biogas conversion factor
        f_b_cf = self.dry_solid_concentration * self.volatile_solid_concentration \
                 * self.volatile_solid_destruction_rate * self.specific_gas_production  # formula explained above

        return diameter, volume_total, f_b_cf, surface_area_total, filled_up_volume, olr, volumetric_flow
