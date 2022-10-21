# this script creates a function for calculating the microclimatic effect of agrivoltaics using calibration
# based on measurement data at APV Resola Hegelbach; 30 min temperature of 2018_corrected (Uni Hohenheim).
# The calibration so far only applies
# for a row distance of 9m as it is in Hegelbach

import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate

data = pd.read_csv(r"apv_microclimate_calibration_dataset_2017.csv")

calibration_temperatures = data["REF_at"]
measured_data = data["APV_at"]

f = interpolate.interp1d(calibration_temperatures, measured_data, fill_value="extrapolate")
other_temperatures = [5, -8, 9, 33]

#data["REF_at"]

data_for_given_other_temperatures = f(other_temperatures)
plt.plot(calibration_temperatures, measured_data, 'o', other_temperatures, data_for_given_other_temperatures, '-')

plt.show()
