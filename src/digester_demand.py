# we assume : electrical energy needed to mix the sludge is 5.27- 7.9 W/𝑚3
#            : electrical energy needed to pump is 150 w/m3
# (source: A.E. Joauhari et al., 2021,Final Project, Beirut Arab University)
# SED is the specific energy demand

class heat_calculation:
    # calculates the heat demand of a anaerobic digester in a specific hour
    def __init__(self, temp_ambient, heat_transfer_coefficient, temp_digester, surface_area,
                 heat_capacity, om_flow):
        self.temp_ambient = temp_ambient
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.temp_digester = temp_digester
        self.surface_area = surface_area
        self.heat_capacity = heat_capacity
        self.om_flow = om_flow


    def compute(self):
        heating = self.om_flow * self.heat_capacity * (self.temp_digester - self.temp_ambient)
        heat_loss = self.heat_transfer_coefficient * self.surface_area * (
                    self.temp_digester - self.temp_ambient) #[W]
        heat_demand = heating + heat_loss
        return heat_demand


class electricity_calculation:
    # calculates the electricity demand of the anaerobic digester
    def __init__(self, wastewater):
        self.wastewater = wastewater

    def compute(self):
        sed_mixing = 7.9 #electricity demand for mixing of the organic matter in the digester [kW]
        sed_pumping = 150 #electricity demand for pumping the organic matter flow [kW]
        electrical_demand = self.wastewater * sed_mixing * sed_pumping
        return electrical_demand
