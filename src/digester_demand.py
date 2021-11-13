# we assume : electrical energy needed to mix the sludge is 5.27- 7.9 W/kg
#            : electrical energy needed to pump the sludge is 150 W/kg
# (source: A.E. Joauhari et al., 2021,Final Project, Beirut Arab University)
# SED is the specific energy demand

class HeatCalculation:
    # calculates the heat demand [kWh] of a anaerobic digester in a specific hour
    def __init__(self, temp_ambient, heat_transfer_coefficient, temp_digester, surface_area,
                 heat_capacity, om_flow):
        self.temp_ambient = temp_ambient
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.temp_digester = temp_digester
        self.surface_area = surface_area
        self.heat_capacity = heat_capacity
        self.om_flow = om_flow

    def compute(self):
        # conversion factors
        cf_jtokwh = 1/3600000
        cf_whtokwh = 1/1000
        heating = self.om_flow * self.heat_capacity * (self.temp_digester - self.temp_ambient) * cf_jtokwh
        heat_loss = self.heat_transfer_coefficient * self.surface_area * (
                    self.temp_digester - self.temp_ambient) * cf_whtokwh
        heat_demand = heating + heat_loss  # kWh
        return heat_demand


class ElectricityCalculation:
    # calculates the electricity demand of the anaerobic digester
    def __init__(self, om_flow, filled_up_volume):
        self.om_flow = om_flow
        self.filled_up_volume = filled_up_volume

    def compute(self):

        sed_mixing = 0.0079 * self.filled_up_volume    # electricity demand for mixing
        # of the organic matter in the digester [kWh],assuming 7.9 W/m³ (Jouahuri et al. 2021)
        sed_pumping = 0.0283 * self.om_flow            # electricity demand for pumping the organic matter flow,
        # assuming 28.3 Wh/kg (Jouahuri et al. 2021)
        electricity_demand = sed_mixing + sed_pumping  # [kWh/h]
        return electricity_demand
