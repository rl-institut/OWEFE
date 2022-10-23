# converting ERA5 nc-File to csv in order to use it in oemof simulation;
# data type conversion shall be automatized in future versions

import xarray as xr
import pandas as pd

# soil moisture

ds = xr.open_dataset('era5_vwc.nc')
vwc_df_area = ds.to_dataframe()
# select data for location_latitude = 47.9, longitude = 9.1
vwc_df = vwc_df_area.iloc[35040:43800,:].copy()

# add volumetric water content (vwc) in root zone depth (rzd), with rzd = 1000 mm; arithmetically averaged according
# the ranges of swvl1, swvl2, swvl3, swvl4
vwc_df["vwc_rzd"] = 0.07*vwc_df.swvl1+0.21*vwc_df.swvl2+0.72*vwc_df.swvl3

vwc_df.to_csv("era5_vwc.csv", index=True)

#  potential evapotranspiration [m]

ds = xr.open_dataset('era5_et0.nc')
et0_df_area = ds.to_dataframe()
# select data for location_latitude = 47.9, longitude = 9.1
et0_df = et0_df_area.iloc[35040:43800,:].copy()

et0_df.to_csv("era5_et0.csv", index=True)
