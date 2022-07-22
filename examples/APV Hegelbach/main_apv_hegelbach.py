# Basic Agrivoltaics Model (Version 0.1) - Case Study of Hegelbach
# import csv
import math

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

# Plant characterisitcs
# winter_wheat
light_saturation_point = 5000  # [lux]

# Create Geometry & solar distribution by using bifacial_radiance
# (inspired by Tutorial 11 - Advanced topics - AgriPV Systems,
# available online: https://github.com/NREL/bifacial_radiance/tree/main/docs/tutorials)

testfolder = Path().resolve() / 'Geometry' / 'TEMP' / 'T1'

print("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
# Create a Radiance Object
demo = RadianceObj('T1', str(testfolder))

# Make Module

# Module Parameters
moduletype='APV_2_UP'
numpanels = 2  # Number of modules arrayed in the Y-direction
x=1.001  # Width of module along the axis of the torque tube or rack. (m)
y=1.675  # Length of module (m) Source, Module Parameters Source: Riedelsheimer (2021)
# Making module with set parameters
module=demo.makeModule(name=moduletype,x=x,y=y,numpanels=numpanels)
print(module)

# Make Scene
# SceneDict Parameters # Source Scene Parameters: Riedelsheimer (2021)
pitch = 9.5  # row distance [m], stated outside of dictionary because it is used below for ground irradiance calculation
tilt = 20    # in degrees
clearance_height = 5  # [m]
azimuth = 225  # in degrees
nMods = 24  # number of modules
nRows = 15  # number of rows
sceneDict = {'tilt': tilt, 'pitch': pitch, 'clearance_height': clearance_height, 'azimuth': azimuth, 'nMods': nMods, 'nRows': nRows}
# Create Scene Object
scene = demo.makeScene(module, sceneDict)

# Set Ground
albedo = 0.2  # 'grass'     # ground albedo
demo.setGround(albedo)

# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 47.9, lon = 9.1)  # This location corresponds to Hegelbach, Germany
# Read in the weather data pulled in above.
metdata = demo.readWeatherFile(epwfile, coerce_year=2017)
# Generate the Sky
demo.genCumSky() # entire year.

# Combine ground, sky, and scene objects
octfile = demo.makeOct()

# demo.getfilelist()  # see what files got merged into the octfile
demo.getfilelist()

# Analyze and get Results

analysis = AnalysisObj(octfile, "on_module")
frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, "on_module", frontscan, backscan)

# Adding the structure -> simplification -> no structure

# Analyse Ground Irradiance

analysis = AnalysisObj(octfile, "ground")
sensorsy = 1
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)

groundscan = frontscan
groundscan['zstart'] = 0.05  # measurements 5 cm above the ground
groundscan['ystart'] = 0  # groundscan in center of APV plant below Modules (row 8)
groundscan['xstart'] = 0  # groundscan in center of APV plant below Modules (row 8)
#  Measurements along azimuth of APV Plant south/west direction
#  groundscan['zinc'] = 0   # height measurement remains constant
#  groundscan['yinc'] = -((math.cos(tilt)*(numpanels*y)+pitch*(nRows-1))/sensorsy)
#  groundscan['xinc'] = -((math.cos(tilt)*(numpanels*y)+pitch*(nRows-1))/sensorsy)

analysis.analysis(octfile, "ground", groundscan, backscan)

logging.info("Create iWEFEs elements")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create solar energy bus on module
bsem = solph.Bus(label="solar energy bus module")

# create solar energy bus on ground
bseg = solph.Bus(label="solar energy bus ground")

# create DC electricity bus
bec = solph.Bus(label="electricity bus")

# create Biomass Bus
bb = solph.Bus(label="biomass bus")

# add buses to the iWEFEs
energysystem.add(bsem, bseg, bec, bb)

# Resources

# solar radiation from the sun
energysystem.add(
    solph.Source(
        label="Sun_module",
        outputs={bsem: solph.Flow(fix=data["BHI"], nominal_value=1)})),

energysystem.add(
    solph.Source(
        label="Sun_ground",
        outputs={bseg: solph.Flow(fix=data["BHI"], nominal_value=1)})),

# CO2 from the atmosphere
# dew
# irrigation
# precipitation
# fertilizer


energysystem.add(
    solph.Transformer(
        label="Solar Energy System",
        inputs={bsem: solph.Flow()},
        outputs={bec: solph.Flow()},
        conversion_factors={bec: 0.17*0.9},  # efficiency PV Panels: 17%, efficiency Inverter: 90 %
    )
)


energysystem.add(
    solph.Transformer(
        label="Plants",
        inputs={bseg: solph.Flow()},
        outputs={bb: solph.Flow()},
        conversion_factors={bb: 120},  # conversion factor solar irradiance [W/m²] -> lux [lumen/m²]
        # light saturation points are given in lux
    )
)

# grid
energysystem.add(solph.Sink(label="grid", inputs={bec: solph.Flow()}))

# biomass processing
energysystem.add(solph.Sink(label="biomass processing", inputs={bb: solph.Flow(nominal_value=1, max=10000, min=0)}))

#create excess sink to represent unused solar energy excess by plants
energysystem.add(solph.Sink(label="excess solar plant", inputs={bb: solph.Flow()}))

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
solar_bus_module = solph.views.node(results, "solar energy bus module")
solar_bus_ground = solph.views.node(results, "solar energy bus ground")
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
solar_bus_module["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)
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
plt.title("received solar irradiance")
plt.xlabel("Time Period [h]")
plt.ylabel("[lux=lumen/m²]")
plt.show()