# Following El Joauhari et al. 2021) we assume:
#            - electrical energy needed to mix the sludge is 5.27- 7.9 W/m³ volumetric flow
#            - constant power application of 1.2 kW to pump 1 m³/day
#            (daily electricity demand: 1.2 kW * 24h * 1/m³) using a progressive cavity pump from FlowRox
#            - constant power to pumped volume ratio
# SED is the specific energy demand

class HeatCalculation:
    # calculates the heat demand [kWh] of a anaerobic digester in a specific hour
    def __init__(self, temp_ambient, heat_transfer_coefficient, temp_digester, surface_area,
                 heat_capacity, average_mass_flow):
        self.temp_ambient = temp_ambient
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.temp_digester = temp_digester
        self.surface_area = surface_area
        self.heat_capacity = heat_capacity
        self.average_mass_flow = average_mass_flow
# average_mass_flow = current mass flow due to steady state operation of the digester, Unit: [kg/h]

    def compute(self):
        # conversion factors
        cf_jtokwh = 1/3600000  # Joule to kWh
        cf_whtokwh = 1/1000  # Wh to kWh
        heating = self.average_mass_flow * self.heat_capacity * (self.temp_digester - self.temp_ambient) * cf_jtokwh
        heat_loss = self.heat_transfer_coefficient * self.surface_area * (
                    self.temp_digester - self.temp_ambient) * cf_whtokwh
        heat_demand = heating + heat_loss  # kWh
        return heat_demand


class ElectricityCalculation:
    # calculates the electricity demand of the anaerobic digester
    def __init__(self, average_volumetric_flow, active_volume):
        self.average_volumetric_flow = average_volumetric_flow  # [m³/h]
        self.average_daily_volumetric_flow = average_volumetric_flow * 24
        self.active_volume = active_volume

    def compute(self):

        sed_mixer = 0.0079 * self.average_volumetric_flow    # [kW] constant power of mixer
        # of the organic matter in the digester,assuming 7.9 W/m³ & constant filling level
        sed_pump = 1.2 * self.average_daily_volumetric_flow  # [kW] constant power of pump
        # El Joauhari et al. (2021) express pump power requirement
        # in constant power to apply over 24 hours to pump average daily volumetric flow [kW/m³daily]
        electricity_demand = sed_mixer + sed_pump  # [kWh] components work constantly over the hour
        return electricity_demand
