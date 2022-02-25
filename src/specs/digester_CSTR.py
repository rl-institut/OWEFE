# Continuos Stirred Tank Reactor Digester Model, geometry and approach for biogas production calculation by
# El Joauhari et al. (2021)

"""
    ********** Digester Type ************
    Digester Type: Continuous Stirred Tank Reactor (CSTR)

   - open systems: material is free to enter or exit the system
   - operate on a steady-state basis: the conditions in the reactor don't change with time
   - reactants are continuously introduced into the reactor while products are continuously removed
   - well mixed -> uniform properties
   Source: University of Michigan, available online:
    https://encyclopedia.che.engin.umich.edu/Pages/Reactors/CSTR/CSTR.html

    ********** Geometry ************
    The CSTR digester is represented as a Cylinder with rounded top and a conic bottom
    Active depth (ad) is calculated directly from the radius and the volume assuming a fixed height:radius ratio of 2:1
    there are additional depths for grit deposit, scum blanket, and space below cover at maximum filling level;
    each measuring 0.15*active depth
    the conic bottom has a slope of 1/5; slope = h/R; and thus adds a depth of 1/5r
    Volume & surface area calculation follows the cylinder and cone geometry laws;

     ******** calculation of feedstock to biogas conversion factor********
    biogas production [m³/h] = mf * sds * svs * rvsd * sgp
    where,
    mf = feedstock mass_flow [kg/h]
    sds = share of dry solids in feedstock
    svs =share of volatile solids in dry solid
    rvsd = volatile solid destruction rate
    sgp = specific gas production for destroyed volatile solids for chosen feedstock [m³/kg]
    feedstock to biogas conversion factor: f_b_cf = sds * svs * rvsd * sgp

"""

import math


class Digester:
    def __init__(self, retention_time, design_mass_flow, sludge_density,
                 sludge_specific_gravity, dry_solid_concentration, volatile_solid_concentration, biomethane_potential):
        self.retention_time = retention_time
        self.design_mass_flow = design_mass_flow
        self.sludge_density = sludge_density
        self.sludge_specific_gravity = sludge_specific_gravity
        self.dry_solid_concentration = dry_solid_concentration
        self.volatile_solid_concentration = volatile_solid_concentration
        self.biomethane_potential = biomethane_potential

    def compute(self):
        volumetric_flow = self.design_mass_flow * 24 / (self.sludge_density * self.sludge_specific_gravity)
        active_volume = volumetric_flow * self.retention_time  # assuming continuous & constant input of
        # dewatered sludge -> filled up volume is constant

        # digester volume
        volume_total = volumetric_flow * self.retention_time
        # digester geometry
        radius = (volume_total/(2*math.pi))**(1/3)  # rearranged cylindric volume formula;
        # assuming a fixed active depth : radius ratio of 2:1 (El Jouahari et al. 2021)
        diameter = 2*radius
        active_depth = 2*radius
        total_sidewall_height = 1.45 * active_depth #
        # Wall Area
        wall_area = 2*math.pi*radius*total_sidewall_height
        # Surface Area
        roof_area = math.pi * radius**2
        # Floor Area
        cone_height = 0.2*radius
        generatrix = (cone_height**2+radius**2)**(1/2)
        floor_area = math.pi*radius*generatrix
        surface_area_total = wall_area+roof_area+floor_area

        # organic loading rate
        total_dry_solids = 0.15 * self.design_mass_flow  # [kg/h]
        total_vs_loading = 0.7 * total_dry_solids  # [kg/h], total volatile solid loading
        olr = total_vs_loading / active_volume * 24  # [kg vs/m³.d], organic loading rate


        # feedstock to biogas conversion factor; calculation over BMP (Biomethane potential)
        f_b_cf = self.dry_solid_concentration * self.volatile_solid_concentration * self.biomethane_potential
        return diameter, volume_total, f_b_cf, surface_area_total, active_volume, olr, volumetric_flow
