# converting ERA5 nc-File to csv in order to use it in oemof simulation;
# data type conversion shall be automatized in future versions

import xarray as xr
import pandas as pd

ds = xr.open_dataset('ERA5_pvlib_2017.nc')
climate_df = ds.to_dataframe()

# add temperature in Celsius row
climate_df["t_air"] = climate_df["t2m"]-273.15
# unit conversion solar irradiance

climate_df["dirhi"] = (climate_df.fdir / 3600.0)
climate_df["ghi"] = (climate_df.ssrd / 3600.0)
climate_df["dhi"] = (climate_df.ghi - climate_df.dirhi)

climate_df.to_csv("ERA5_pvlib_2017.csv", index=True)
