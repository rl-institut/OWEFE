# this script creates a function for calculating the microclimatic effect of agrivoltaics on temperature
# on the ground below the photovoltaic panels using calibration
# based on measurement data at APV Resola Hegelbach; 30 min temperature of 2017 (Uni Hohenheim).
# Limitation: The calibration so far only applies for a row distance of 9m, as it is in the case study Hegelbach

# soil moisture calibration dataset:
# from 10.12.2018, 10:30:00 until 14.12.2018 08:00:00; data from 2017 was used to fill in incomplete 2018 dataset

import matplotlib.pyplot as plt

import pandas as pd
from scipy import interpolate

# load calibration dataset
data = pd.read_csv(r"apv_microclimate_calibration_soil_moisture_dataset_2018.csv")
# load data to be calibrated
era5_vwc = pd.read_csv(r"era5_vwc.csv")

# determine calibration data series and measurement data series
calibration_data = data["REF_vwc"]
measured_data = data["APV_vwc"]
# setup calibration function
f = interpolate.interp1d(calibration_data, measured_data, fill_value="extrapolate")
other_data = era5_vwc["vwc_rzd"]
calibrated_data = f(other_data)

# plot calibration data
plt.plot(calibration_data, measured_data, 'o', other_data, calibrated_data, '-')
plt.show()

# Resample data: 30 min to H

index = pd.date_range('1/1/2018', periods=17520, freq='30T')
calibrated_vwc_df = pd.DataFrame(data=calibrated_data, index=index, columns=['t_air'])
calibrated_vwc_df_H = calibrated_vwc_df.resample('H').mean()
#  data_apv_H_list = data_apv_H.values.tolist()
#  t_air_below_pv = pd.DataFrame(calibrated_data, columns=["Value"])
calibrated_vwc_df_H.to_csv("calibrated_vwc_below_apv_2018.csv", index=True)
