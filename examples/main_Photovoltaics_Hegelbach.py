# Basic Photovoltaic Model
#import csv
#import math

from oemof.tools import logger
from oemof import solph


import logging
import os
import pandas as pd
import pprint as pp
import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

solver = "cbc"
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 24 * 7 * 8
solver_verbose = False  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_example.log",
    screen_level=logging.INFO,
    file_level=logging.DEBUG,
)
print(number_of_time_steps)

# create integrated Water-Energy-Food-Eco System (iWEFEs)
logging.info("Initialize the energy system")
date_time_index = pd.date_range(
    "1/1/2018", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# Read input data file

data = pd.read_csv(r"apv_hegelbach_raw.csv")
print(data["BHI"])

# Create oemof objects bus, sink , source, transformer...

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
        outputs={bsed: solph.Flow(fix=data["BHI"])})),

# dew
# irrigation
# precipitation
# fertilizer


energysystem.add(
    solph.Transformer(
        label="Photovoltaic Panels",
        inputs={bsed: solph.Flow()},
        outputs={bedc: solph.Flow()},
        conversion_factors={bedc: 0.17},
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
energysystem.add(solph.Sink(label="electricity demand", inputs={beac: solph.Flow()}))


##########################################################################
# Optimise the energy system and plot the results
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


#  print the solver results
print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

print("********* Main results *********")

# plot data
if plt is not None:
    # # plot PQ diagram from component results
    # data = results[(bpt, None)]["sequences"]
    # ax = data.plot(kind="scatter", x="Q", y="P", grid=True)
    # ax.set_xlabel("Q (MW)")
    # ax.set_ylabel("P (MW)")
    # plt.show()

    # plot thermal bus
    data = solph.views.node(results, "bth")["sequences"]
    ax = data.plot(kind="line", drawstyle="steps-post", grid=True)
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Q (MW)")
    plt.show()
plt.show()
