# we assume : electrical energy needed to mix the sludge is 5.27- 7.9 W/𝑚3
#            : electrical energy needed to pump is 150 w/m3
# (source: A.E. Joauhari et al., 2021,Final Project, Beirut Arab University)
# SED is the specific energy demand

class heat_calculation:
    def __init__(self, temp_ambient, heat_transfer_coefficient, temp_digester, surface_area_total_overground):
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.temp_digester = temp_digester
        self.temp_ambient = temp_ambient
        self.surface_area_total_overground = surface_area_total_overground

    def compute(self):
        heat_demand = self.heat_transfer_coefficient * self.surface_area_total_overground * (
                    self.temp_digester - self.temp_ambient)
        return heat_demand


class electricity_calculation:
    def __init__(self, wastewater):
        self.wastewater = wastewater

    def compute(self):
        SED_mixing = 7.9
        SED_pumping = 150
        electrical_demand = self.wastewater * SED_mixing * SED_pumping
        return electrical_demand