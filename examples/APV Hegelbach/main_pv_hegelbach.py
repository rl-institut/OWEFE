# Basic Photovoltaic Model
# import csv
# import mat

from oemof.tools import logger
from oemof import solph


import logging
import os
import pandas as pd
import pprint as pp
import xarray as xr
import numpy as np

# changing working directory to use module from source
os.chdir("../../src")

import src.specs.photovoltaic_panel as photovoltaic_panel
os.chdir("../examples/APV Hegelbach")

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
    "1/1/2017", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# *********************************************************************************************
# inputs
# *********************************************************************************************
# Read input data file
data = pd.read_csv(r"apv_hegelbach_raw.csv")
climate_df = pd.read_csv('ERA5_pvlib_2017.csv')
print(list(data.columns.values))
print(list(climate_df.columns.values))
latitude = 47.9
longitude = 9.1
# define electricity demand curve and set it to same
electricity_demand = pd.Series([1, 1, 1, 1, 1, 3, 5, 7, 12, 6, 4, 4, 9, 14, 8, 3, 4, 4, 9, 10, 6, 5, 3, 2],
                               index=date_time_index, name="electricity demand")
# define ambient temperature panda series
temp = pd.Series([10, 14, 12, 12, 14, 16, 17, 19, 20, 23, 25, 27, 29, 30, 31, 31, 29, 26, 24, 22, 20, 19, 17, 16],
                 index=date_time_index, name="ambient temperature")
# *********************************************************************************************
# Component Characteristics
# *********************************************************************************************
# Photovoltaic Panel Characteristics
# module_name = "SolarWorld SW 270 duo bifacial PV" Source: Schindele et al. 2020
# module_area = 1206 [m²], Source: Schindele et al. 2020
p_rpv = 270  # [Wp]
r_ref = 1000  # [W/m²]
n_t = -0.0037  # [1/°C], Value Source: Maleki et al. (2015), Ismail et al. (2013)
t_c_ref = 25  # [°C]
noct = 48  # [°C]
# *********************************************************************************************
# define iWEFEs/Create oemof objects (bus, sink , source, transformer....)
# *********************************************************************************************
logging.info("Create oemof objects")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create solar energy distribution bus
bsed = solph.Bus(label="solar energy bus")

# create DC electricity bus
bedc = solph.Bus(label="DC electricity bus")

# create AC electricity bus
beac = solph.Bus(label="AC electricity bus")

# add buses to the iWEFEs
energysystem.add(bsed, bedc, beac)

# Resources

# solar radiation
energysystem.add(
    solph.Source(
        label="solar",
        outputs={bsed: solph.Flow(fix=climate_df["ssrd"], nominal_value=1)})),

# dew
# irrigation
# precipitation
# fertilizer
# photovoltaic panels
pv_te = photovoltaic_panel.calc_pv_te(
    t_air=climate_df["t_air"], ghi=climate_df["ghi"], p_rpv=p_rpv, r_ref=r_ref, n_t=n_t, t_c_ref=t_c_ref, noct=noct)
energysystem.add(
    solph.Transformer(
        label="Photovoltaic Panels",
        inputs={bsed: solph.Flow()},
        outputs={bedc: solph.Flow()},
        conversion_factors={bedc: pv_te},
    )
)


energysystem.add(
    solph.Transformer(
        label="Inverter",
        inputs={bedc: solph.Flow()},
        outputs={beac: solph.Flow()},
        conversion_factors={beac: 0.9},
    )
)

# electricity production
energysystem.add(solph.Sink(label="electricity production", inputs={beac: solph.Flow()}))


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
ac_electricity_bus = solph.views.node(results, "AC electricity bus")
solar_bus = solph.views.node(results, "solar energy bus")

# ***************************************************************************
#  print the results
# ***************************************************************************

print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

print("********* Main results *********")
pp.pprint(energysystem.results["main"])

# print("-----------")
# print(ac_electricity_bus["sequences"].sum(axis=0))
# print(type(ac_electricity_bus["sequences"].sum(axis=0).to_numpy()))
# print(ac_electricity_bus["sequences"].sum(axis=0).to_numpy())
# print("----------")

# ***************************************************************************
#  plot the results
# ***************************************************************************

# plot electricity production from solar input and electricity demand

fig, ax = plt.subplots(figsize=(10, 5))
ac_electricity_bus["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)
solar_bus["sequences"].plot(
    ax=ax, kind="line", drawstyle="steps-post"
)
electricity_demand.plot(
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

