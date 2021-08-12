import math


class Digester:
    def __init__(self, height, retention_time):
        self.height = height
        self.retention_time = retention_time

    def compute(self, yield_factor=7.15):
        height1 = 0.3 * self.height  # height for gas storage
        height2 = 0.7 * self.height  # height for digester volume
        diameter = 2 * self.height
        radius = diameter/2
        volume = (math.pi * pow(radius, 2) * height1 / 3) + (math.pi * pow(radius, 2) * height2)
        if self.retention_time > 30: #retention_time in days
            yield_factor = 6.4
        conv_factor = (volume * yield_factor) / 1000
        return volume, conv_factor
