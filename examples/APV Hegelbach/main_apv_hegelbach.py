# Basic Agrivoltaics Model (Version 0.1) - Case Study of Hegelbach
# import csv
# import mat

from oemof.tools import logger
from oemof import solph

import logging
import os
from pathlib import Path
import pandas as pd
import pprint as pp

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

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
# define electricity demand curve and set it to same
electricity_demand = pd.Series([1, 1, 1, 1, 1, 3, 5, 7, 12, 6, 4, 4, 9, 14, 8, 3, 4, 4, 9, 10, 6, 5, 3, 2],
                               index=date_time_index, name="electricity demand")
# *********************************************************************************************
# define geometry and iWEFEs elements
# *********************************************************************************************
# Create Geometry

testfolder = Path().resolve() / 'APV_Solar_Irradiance_Simulation' / 'TEMP' / 'Geometry_1'

print("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('bifacial_example',str(testfolder))

# Input albedo number or material name like 'concrete'.
demo.setGround()  # This prints available materials.
albedo = 0.62
demo.setGround(albedo)
# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 47.9, lon = 9.1)  # This location corresponds to Hegelbach, Germany
# Read in the weather data pulled in above.
metdata = demo.readWeatherFile(epwfile, coerce_year=2017)
# Generate the Sky
fullYear = True
if fullYear:
    demo.genCumSky() # entire year.
else:
    timeindex = metdata.datetime.index(pd.to_datetime('2017-06-17 12:0:0 -7'))
    demo.gendaylit(timeindex)  # Noon, June 17th (timepoint # 4020)

# Define a module type
module_type = 'test-module'
module = demo.makeModule(name=module_type,x=1.695, y=0.984)
print(module)
availableModules = demo.printModules()

# Make the scene
sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7}  # set scene parameters
scene = demo.makeScene(module,sceneDict)  # create scene object

# Combine ground, sky, and scene objects
octfile = demo.makeOct(demo.getfilelist())

# demo.getfilelist()  # see what files got merged into the octfile

# Analyze and get Results

analysis = AnalysisObj(octfile, demo.basename)
analysis = AnalysisObj(octfile, demo.basename)


logging.info("Create iWEFEs elements")




# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create solar energy bus
bse = solph.Bus(label="solar energy bus")

# create DC electricity bus
bec = solph.Bus(label="electricity bus")

# create Biomass Bus
bb = solph.Bus(label="biomass bus")

# add buses to the iWEFEs
energysystem.add(bse, bec, bb)

# Resources

# solar radiation from the sun
energysystem.add(
    solph.Source(
        label="Sun",
        outputs={bse: solph.Flow(fix=data["BHI"], nominal_value=1)})),

# CO2 from the atmosphere
# dew
# irrigation
# precipitation
# fertilizer


energysystem.add(
    solph.Transformer(
        label="Solar Energy System",
        inputs={bse: solph.Flow()},
        outputs={bec: solph.Flow()},
        conversion_factors={bec: 0.17*0.9},  # efficiency PV Panels: 17%, efficiency Inverter: 90 %
    )
)


energysystem.add(
    solph.Transformer(
        label="Plants",
        inputs={bse: solph.Flow()},
        outputs={bb: solph.Flow()},
        conversion_factors={bb: 0.1},
    )
)

# grid
energysystem.add(solph.Sink(label="grid", inputs={bec: solph.Flow()}))

# biomass processing
energysystem.add(solph.Sink(label="biomass processing", inputs={bb: solph.Flow()}))

##########################################################################
# Simulate the iWEFEs and plot the results
##########################################################################

logging.info("Optimise the energy system")

# initialise the operational model
model = solph.Model(energysystem)

# This is for debugging only. It is not(!) necessary to solve the problem and
# should be set to False to save time and disc space in normal use. For
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

logging.info("Store the energy system with the results.")

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
electricity_bus = solph.views.node(results, "electricity bus")
solar_bus = solph.views.node(results, "solar energy bus")
biomass_bus = solph.views.node(results, "biomass bus")

# ***************************************************************************
#  print the results
# ***************************************************************************

print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

print("********* Main results *********")
pp.pprint(energysystem.results["main"])

print("-----------")
print(electricity_bus["sequences"].sum(axis=0))
print(type(electricity_bus["sequences"].sum(axis=0).to_numpy()))
print(electricity_bus["sequences"].sum(axis=0).to_numpy())
print("----------")

# ***************************************************************************
#  plot the results
# ***************************************************************************

# plot electricity production from solar input and electricity demand

fig, ax = plt.subplots(figsize=(10, 5))
electricity_bus["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)
solar_bus["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)

plt.legend(
    loc="upper center",
    prop={"size": 8},
    bbox_to_anchor=(0.5, 1.3),
    ncol=3,
)
fig.subplots_adjust(top=0.8)
plt.title("Electricity Production and Demand")
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
plt.title("Biomass Production")
plt.xlabel("Time Period [h]")
plt.ylabel("Biomass [kg]")
plt.show()