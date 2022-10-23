# this script creates a function for calculating the microclimatic effect of agrivoltaics on temperature
# on the ground below the photovoltaic panels using calibration
# based on measurement data at APV Resola Hegelbach; 30 min temperature of 2017 (Uni Hohenheim).
# Limitation: The calibration so far only applies for a row distance of 9m, as it is in the case study Hegelbach

import matplotlib.pyplot as plt

import pandas as pd
from scipy import interpolate

# load calibration dataset
data = pd.read_csv(r"apv_microclimate_calibration_dataset_2017.csv")
# load data to be calibrated
climate_df = pd.read_csv(r"ERA5_pvlib_2018.csv")

# determine calibration data series and measurement data series
calibration_temperatures = data["REF_at"]
measured_data = data["APV_at"]
# setup calibration function
f = interpolate.interp1d(calibration_temperatures, measured_data, fill_value="extrapolate")
other_temperatures = climate_df["t_air"]
calibrated_data = f(other_temperatures)

# plot calibration data
plt.plot(calibration_temperatures, measured_data, 'o', other_temperatures, calibrated_data, '-')
plt.show()

# Resample data: 30 min to H

index = pd.date_range('1/1/2018', periods=17520, freq='30T')
calibrated_data_df = pd.DataFrame(data=calibrated_data, index=index, columns=['t_air'])
calibrated_data_df_H = calibrated_data_df.resample('H').mean()
#  data_apv_H_list = data_apv_H.values.tolist()
#  t_air_below_pv = pd.DataFrame(calibrated_data, columns=["Value"])
calibrated_data_df_H.to_csv("t_air_below_apv_calibrated_2018.csv", index=True)

print(calibrated_data_df_H)
