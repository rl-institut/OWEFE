import os

import numpy as np
import pandas as pd
from feedinlib import era5
from feedinlib.powerplants import Photovoltaic
from feedinlib.cds_request_tools import get_cds_data_from_datespan_and_position
# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# define photovoltaic system
system_data = {
    'module_name': 'Advent_Solar_Ventura_210___2008_',  # module name as in database
    'inverter_name': 'ABB__MICRO_0_25_I_OUTD_US_208__208V_',  # inverter name as in database
    'azimuth': 180,
    'tilt': 30,
    'albedo': 0.2}
# create photovoltaic object
pv_system = Photovoltaic(**system_data)
print(pv_system)

# load weather data
from feedinlib.open_FRED import Weather
from feedinlib.open_FRED import defaultdb
from shapely.geometry import Point

latitude = 47.9
longitude = 9.1
location = Point(longitude,latitude)
solar_hegelbach = pd.read_csv(r"apv_hegelbach_raw.csv")
# download weather data

# ERA5
# set start and end date (end date will be included
# in the time period for which data is downloaded)
start_date, end_date = '2017-01-01', '2017-12-31'
# set variable set to download
variable = "pvlib"
target_file = 'ERA5_pvlib_2017.nc'

#ds = era5.get_era5_data_from_datespan_and_position(
#    variable=variable,
#    start_date=start_date, end_date=end_date,
#    latitude=latitude, longitude=longitude,
#    target_file=target_file)


#open_FRED_weather_data = Weather(
#    start='2017-01-01', stop='2017-12-31',
#   locations=[location],
#    variables="pvlib",
#    **defaultdb())
# get weather data in pvlib format
# weather_df = open_FRED_weather_data.df(location=location, lib="pvlib")
# plot irradiance
# import matplotlib.pyplot as plt
# weather_df.loc[:, ['BHI', 'DHI']].plot(title='Irradiance')
# plt.xlabel('Time')
# plt.ylabel('Irradiance in $W/m^2$')






