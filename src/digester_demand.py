# we assume : electrical energy needed to mix the sludge is 5.27- 7.9 W/m³ filled up volume
#            : electrical energy needed to pump is 28.15 Wh/kg dewatered; assuming a sludge densitiy of 997 kg/m³,
#            and applying a progressive cavity pump from FlowRox
#            assuming that it requires a constant power application of 1.2 kW to pump 1 m³/day;
#            with a constant power to pumped volume relation

# (source: A.E. Joauhari et al., 2021,Final Project, Beirut Arab University)
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
    def __init__(self, average_mass_flow, active_volume):
        self.average_mass_flow = average_mass_flow
        self.active_volume = active_volume

    def compute(self):

        sed_mixing = 0.0079 * self.active_volume    # electricity demand for mixing
        # of the organic matter in the digester [kWh],assuming 7.9 W/m³ & constant filling level
        # (Final Year Project, Beirut Arab University 2021)
        sed_pumping = 0.02815 * self.average_mass_flow
        # electricity demand for pumping the organic matter flow,
        # assuming 28.15 Wh/kg (Joauhari et al., 2021)
        # print(sed_mixing)
        # print(sed_pumping)
        electricity_demand = sed_mixing + sed_pumping  # [kWh/h]
        return electricity_demand
