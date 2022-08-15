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
pvlib_df = era5.weather_df_from_era5(
    era5_netcdf_filename=era5_netcdf_filename,
    start=start_date,
    end=end_date,
    lib='pvlib',
    area=[longitude, latitude],
)

# plot irradiance
# import matplotlib.pyplot as plt
# weather_df.loc[:, ['BHI', 'DHI']].plot(title='Irradiance')
# plt.xlabel('Time')
# plt.ylabel('Irradiance in $W/m^2$')


from oemof.tools import logger
from oemof import solph

import logging
import os
import pandas as pd


try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# changing cwd to use the function from the main file
os.chdir("../../src")

import src.specs.plant as plant

os.chdir("../examples/APV Hegelbach")

# *********************************************************************************************
# set up oemof.solph
# *********************************************************************************************

solver = "cbc"
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 24
solver_verbose = False  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_example.log",
    screen_level=logging.INFO,
    file_level=logging.DEBUG,
)
print(number_of_time_steps)

logging.info("Initialize the iWEFEs system")
date_time_index = pd.date_range(
    "1/1/2018", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# *********************************************************************************************
# inputs
# *********************************************************************************************
# Read input data file
data = pd.read_csv(r"apv_hegelbach_raw.csv")
# define ambient temperature panda series
temp = pd.Series([5, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 0, 14, 13, 12, 11, 10, 9, 2, 8, 7, 6, 6],
                 index=date_time_index, name="t")
# *********************************************************************************************
# define geometry and iWEFEs elements
# *********************************************************************************************

# Plant characteristics
# Wheat Batten
light_saturation_point = 60000  # [lux]
# Cultivar parameters, source: simple crop model
t_sum = 2150
HI = 0.34
I50A = 280
I50B = 50
# Species Parameters
t_base = 0
t_opt = 15
RUE = 1.24
I50maxH = 100
I50maxW = 25
Tmax = 34
Text = 45
SCO2 = 0.08
Swater = 0.4

logging.info("Create iWEFEs elements")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create solar energy bus on ground
bseg = solph.Bus(label="solar energy bus ground")

# create biomass bus
bb = solph.Bus(label="biomass bus")

# add buses to the iWEFEs
energysystem.add(bseg, bb)

# Resources

energysystem.add(
    solph.Source(
        label="Sun_ground",
        outputs={bseg: solph.Flow(fix=data["BHI"], nominal_value=1)})),


# plant
# temperature effect on biomass growth rate
te = plant.calc_te(temp=temp, t_opt=t_opt, t_base=t_base)
# add plant transformer
print(te)
# plant leaves
energysystem.add(
    solph.Transformer(
        label="plant leafs",
        inputs={bseg: solph.Flow()},
        conversion_factors={bb: te},
        outputs={bb: solph.Flow()},
    )
)

# biomass harvest
energysystem.add(solph.Sink(label="harvest", inputs={bb: solph.Flow()}))


##########################################################################
# Simulate the iWEFEs and plot the results
##########################################################################

logging.info("Optimise the energy system")

# initialise the operational model
model = solph.Model(energysystem)

# This is for debugging only. It is not(!) necessary to solve the problem and
# should be set to false to save time and disc space in normal use. For
# debugging the timesteps should be set to 3, to increase the readability of
# the lp-file.
if debug:
    filename = os.path.join(
        solph.helpers.extend_basic_path("lp_files"), "basic_example.lp"
    )
    logging.info("Store lp-file in {0}.".format(filename))
    model.write(filename, io_options={"symbolic_solver_labels": True})

# if tee_switch is true solver messages will be displayed
logging.info("Solve the optimization problem")
model.solve(solver=solver, solve_kwargs={"tee": solver_verbose})

logging.info("Store the iWEFEs with the results.")

# The processing module of the outputlib can be used to extract the results
# from the model transfer them into a homogeneous structured dictionary.

# add result files
energysystem.results["main"] = solph.processing.results(model)
energysystem.results["meta"] = solph.processing.meta_results(model)

# The default path is the '.oemof' folder in your $HOME directory.
# The default filename is 'es_dump.oemof'.
# You can omit the attributes (as None is the default value) for testing cases.
# You should use unique names/folders for valuable results to avoid
# overwriting.

# store energy system with results
energysystem.dump(dpath=None, filename=None)

# ****************************************************************************
# ********** PART 2 - Processing the results *********************************
# ****************************************************************************

logging.info("**** The script can be divided into two parts here.")
logging.info("Restore the energy system and the results.")
energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

# define an alias for shorter calls below (optional)
results = energysystem.results["main"]

# *****************************************************************************
# get results of a specific component/bus
# *****************************************************************************
solar_bus_ground = solph.views.node(results, "solar energy bus ground")
biomass_bus = solph.views.node(results, "biomass bus")

# ***************************************************************************
#  print the results
# ***************************************************************************

# print("********* Meta results *********")
# pp.pprint(energysystem.results["meta"])
# print("")

# print("********* Main results *********")
# pp.pprint(energysystem.results["main"])


# ***************************************************************************
#  plot the results
# ***************************************************************************

# plot electricity production from solar input and electricity demand

fig, ax = plt.subplots(figsize=(10, 5))
solar_bus_ground["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)
plt.legend(
    loc="upper center",
    prop={"size": 8},
    bbox_to_anchor=(0.5, 1.3),
    ncol=3,
)
fig.subplots_adjust(top=0.8)
plt.title("Solar Energy on Ground")
plt.xlabel("Time Period [h]")
plt.ylabel("Energy [kW]")
plt.show()

fig, ax = plt.subplots(figsize=(10, 5))
biomass_bus["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)
plt.legend(
    loc="upper center",
    prop={"size": 8},
    bbox_to_anchor=(0.5, 1.3),
    ncol=3,
)
fig.subplots_adjust(top=0.8)
plt.title("biomass production rate")
plt.xlabel("Time Period [day]")
plt.ylabel("biomass production rate[g/day]")
plt.show()


# calculate annual production sums
biomass_sum = biomass_bus["sequences"].sum(axis=0)

# calculate harvested biomass
harvest = biomass_sum * HI
print(harvest)





