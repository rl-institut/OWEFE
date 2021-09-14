# average COD (influent) from Anaerobic digester in range 1500 to 2000 mg/L (source: Metcalf and Eddy(2004))
# ratio between BOD / COD (influent) is 0.3 to 0.8
# ratio between BOD / COD (effluent) is 0.1 to 0.3 -> we take avg ratio: 0.5
# For plug flow, BOD5 -> first order kinematics
# K1 -> constant (Reed et al, 1988)
# Hydraulic retention time 4days is highly effective (source: D. Ghosh et al., 2010)
# porosity (typically) 0.4 for 25-mm gravel
# temperature remain constant between 31 - 33 degree Celsius
# Depth of CW (m) = [1 – 1.8m usually]
# net discharge is excluding seepage that is 10% of total discharge
# average nitrate in influent water is assume to 450mg/L (source: case study of FSM in leh town,Ladhak/TUM)
# cw_area multiplied by 24 to convert into day
# net evaporation is calculate in mm/day
# HRT = 4days


import math


class Constructed_wetlands:
    def __init__(self, influent, effluent):
        self.influent = influent * 24
        self.effluent = effluent * 24

    def compute(self):
        depth = 0.6
        porosity = 0.4
        temperature = 35
        COD_influent = 1800
        BOD_influent = COD_influent * 0.5
        NO3_influent = 450
        retention_time = 4
        avg_discharge = (self.influent - self.effluent) / 2
        cw_area = avg_discharge * retention_time / (porosity * depth)
        net_evaporation = (self.influent - self.effluent)/(0.001 * cw_area)
        K1 = 68.6 * porosity ** 4.172 * 1.06 ** (temperature-20)
        a_1 = 2 * porosity * cw_area * depth
        a_2 = (2 * self.influent) - (0.001 * net_evaporation * cw_area)
        a_3 = (a_1/a_2)
        BOD_effluent = BOD_influent * math.exp(-K1*a_3)
        COD_effluent = BOD_effluent * 2
        efficiency = (BOD_effluent - BOD_influent) / BOD_effluent
        BOD_new: float = efficiency * BOD_effluent
        COD_new = float(BOD_new * 2)
        if COD_effluent > 250:
            print(f'COD {COD_effluent} mg/L is higher than the WHO allowable limit {250} mg/L')
            print(f'You need one more Horizontal subsurface constructed wetland')
            BOD_effluent = BOD_new
            COD_effluent = COD_new
            print(f'New COD is {COD_new} mg/L')
        else:
            print(f'The limit is in the range')
        var4 = -0.126 * 1.008 ** (temperature - 20) * retention_time
        NO3_effluent = NO3_influent * math.exp(var4)
        return avg_discharge, cw_area, net_evaporation, BOD_effluent, COD_effluent, NO3_effluent

