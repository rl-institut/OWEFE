# use environment which has feedinlib dev version installed to make script run
# this code is currently not working because feedinlib functions have lost compatibility with pvlib,
# please update feedinlib
import os
import numpy as np
import pandas as pd
import xarray as xr
from feedinlib import era5
from feedinlib import Photovoltaic
from shapely.geometry import Point

# ERA5
# set start and end date (end date will be included
# in the time period for which data is downloaded)
start_date, end_date = '2017-01-01', '2017-12-31'
# set variable set to download
variable = "pvlib"
era5_netcdf_filename = 'ERA5_pvlib_2017.nc'
latitude = 47.9
longitude = 9.1
location = Point(longitude, latitude)
print('ERA5_pvlib_2017.nc')
# single_location = [47.9, 9.1]
climate_df = era5.weather_df_from_era5(
    era5_netcdf_filename=era5_netcdf_filename,
    start=start_date,
    end=end_date,
    lib='pvlib',
    area=[longitude, latitude],
)
climate_df["dni"] = climate_df["ghi"]-climate_df["dhi"]

# define photovoltaic system
system_data = {
    'module_name': 'Advent_Solar_Ventura_210___2008_',  # module name as in database
    'inverter_name': 'ABB__MICRO_0_25_I_OUTD_US_208__208V_',  # inverter name as in database
    'azimuth': 180,
    'tilt': 30,
    'albedo': 0.2}
# create photovoltaic object
pv_system = Photovoltaic(**system_data)
feedin = pv_system.feedin(
    weather = climate_df,
    location = (47.9, 9.1))
feedin.plot()


# plot irradiance
# import matplotlib.pyplot as plt
# weather_df.loc[:, ['BHI', 'DHI']].plot(title='Irradiance')
# plt.xlabel('Time')
# plt.ylabel('Irradiance in $W/m^2$')






