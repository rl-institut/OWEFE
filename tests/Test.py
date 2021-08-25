# Default logger of oemof
import csv
import math

from oemof.tools import logger
from oemof import solph
from digester import Digester
# from nose.tools import eq_
# from oemof.network.network import Node

import logging
import os
import pandas as pd
import pprint as pp

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

solver = "cbc"
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 3
solver_verbose = False  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_example.log",
    screen_level=logging.INFO,
    file_level=logging.DEBUG,
)
print(number_of_time_steps)

# setup an energy system
logging.info("Initialize the energy system")
date_time_index = pd.date_range(
    "1/1/2021", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# Read data file
# filename = os.path.join(os.getcwd(), "basic_example_copy.csv")
data = pd.read_csv(r"basic_example_copy.csv")

# Create oemof objects bus, sink , source, transformer...

logging.info("Create oemof objects")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create influent bus
bsld = solph.Bus(label="sludge")

# create volatile solid bus
bvol = solph.Bus(label="volatile solids")

# create electricity bus
bel = solph.Bus(label="electricity")

# create slurry bus
bslu = solph.Bus(label="slurry")

# create effluent bus
beff1 = solph.Bus(label="effluent1")
beff2 = solph.Bus(label="effluent2")

# create digested bus
bdig = solph.Bus(label="digested")

# create bio-gas bus
bbgas = solph.Bus(label="bio-gas")

bch4 = solph.Bus(label="bio-methane")

# create heat bus
bheat = solph.Bus(label="heat")

# adding the buses to the energy system
energysystem.add(bsld, bel, bslu, beff1, beff2, bvol, bdig, bbgas, bch4, bheat)

# create excess component for the bio-gas bus to allow overproduction
energysystem.add(solph.Sink(label="excess_bio-gas", inputs={bbgas: solph.Flow()}))

# create fixed source object representing domestic sewage
energysystem.add(
    solph.Source(
        label="wastewater",
        outputs={bsld: solph.Flow(fix=data["wastewater"], nominal_value=1000000)},
    )
)

# create sink object representing the electrical demand
energysystem.add(
    solph.Sink(
        label="demand_el",
        inputs={bel: solph.Flow(fix=data["demand_el"], nominal_value=1)},
    )
)

# create sink object representing the thermal demand
energysystem.add(
    solph.Sink(
        label="demand_th",
        inputs={bheat: solph.Flow(fix=data["demand_th"], nominal_value=1)},
    )
)

# create sink object representing the water demand
energysystem.add(
    solph.Sink(
        label="demand_water",
        inputs={beff2: solph.Flow(fix=data["demand_water"], nominal_value=1)},
    )
)

# create sink object representing the fertilizer demand
energysystem.add(
    solph.Sink(
        label="demand_f",
        inputs={bdig: solph.Flow(fix=data["demand_f"], nominal_value=1)},
    )
)


# total height of the digester m, initial concentration of volatile solid in slurry kg/m3, yield factor depends upon retention time
height = 2
retention_time = 30
bg_prod = Digester(height, retention_time)
design_diameter, volume, bg_prod_result = bg_prod.compute()
print('Total design diameter : ', round(design_diameter, 2))
print('Total volume of digester : ', round(volume, 2))
print('biogas conversion factor: ', round(bg_prod_result,2))
#
if bg_prod_result < 0.36:
    print(f'bg_prod_result {bg_prod_result} is too low to proceed')
    raise Exception
elif bg_prod_result > 1:
    print(f'bg_prod_result {bg_prod_result} is too large to proceed')
    raise Exception
# else:
    # bg_prod_result
bg_prod_result = 0.7
# a = bg_prod_result * 3 # bg_prod_result must be at least 0.36

# create simple transformer object representing a gas power plant
# wt. of volatile solids for human waste = 0.03 Kg/day = 0.00125 Kg/hr (source: IRENA statistics 2016)
# initial concentration of volatile solids : kg/ m3
# Bio-gas production : m3/day
# Methane CH4 : m3/day : 1m3 CH4 = 34 MJ : 3.6 MJ = 1 khw

energysystem.add(
    solph.Transformer(
        label="digester_gas",
        inputs={bsld: solph.Flow()},
        outputs={bbgas: solph.Flow(nominal_value=10e5, variable_costs=60)},
        conversion_factors={bbgas: bg_prod_result},
    )
)

energysystem.add(
    solph.Transformer(
        label="Bio - Methane",
        inputs={bbgas: solph.Flow()},
        outputs={bch4: solph.Flow(nominal_value=10e5, variable_costs=60)},
        conversion_factors={bch4: 0.65},
    )
)

energysystem.add(
    solph.Transformer(
        label="CHP_el",
        inputs={bch4: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e5, variable_costs=60)},
        conversion_factors={bel: 0.58},
    )
)

energysystem.add(
    solph.Transformer(
        label="CHP_th",
        inputs={bch4: solph.Flow()},
        outputs={bheat: solph.Flow(nominal_value=10e5, variable_costs=60)},
        conversion_factors={bel: 0.40},
    )
)

energysystem.add(
    solph.Transformer(
        label="digester_slu",
        inputs={bsld: solph.Flow()},
        outputs={bslu: solph.Flow(nominal_value=10e5, variable_costs=60)},
        conversion_factors={bslu: 0.50},
    )
)

energysystem.add(
    solph.Transformer(
        label="dewatering_dig",
        inputs={bslu: solph.Flow()},
        outputs={bdig: solph.Flow(nominal_value=10e2, variable_costs=60)},
        conversion_factors={bdig: 0.42},
    )
)

energysystem.add(
    solph.Transformer(
        label="dewatering_eff",
        inputs={bslu: solph.Flow()},
        outputs={beff1: solph.Flow(nominal_value=10e2, variable_costs=60)},
        conversion_factors={beff1: 0.30},
    )
)

energysystem.add(
    solph.Transformer(
        label="cw",
        inputs={beff1: solph.Flow()},
        outputs={beff2: solph.Flow(nominal_value=10e2, variable_costs=60)},
        conversion_factors={beff2: 0.6},
    )
)

# mean= solph.views.node(outputs, "effluent2")

# create storage object representing a battery
storage = solph.components.GenericStorage(
    nominal_storage_capacity=10077997,
    label="ch4_storage",
    inputs={bch4: solph.Flow()},
    outputs={bch4: solph.Flow(nominal_value=10077997 / 6)},
    loss_rate=0.00,
    initial_storage_level=None,
    inflow_conversion_factor=1,
    outflow_conversion_factor=0.8,
)

energysystem.add(storage)

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

# add results to the energy system to make it possible to store them.
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
storage = energysystem.groups["ch4_storage"]

# print a time slice of the state of charge
print("")
print("********* State of Charge (slice) *********")
print(
    results[(storage, None)]["sequences"][
    "2012-02-25 08:00:00":"2012-02-26 15:00:00"
    ]
)
print("")

# get all variables of a specific component/bus
custom_storage = solph.views.node(results, "ch4_storage")
electricity_bus = solph.views.node(results, "electricity")
heat_bus = solph.views.node(results, "heat")
digested_bus = solph.views.node(results, "digested")
sludge_bus = solph.views.node(results, "sludge")
volatilesolids_bus = solph.views.node(results, "volatile solids")
slurry_bus = solph.views.node(results, "slurry")
bio_gas_bus = solph.views.node(results, "bio-gas")
effluent1_bus = solph.views.node(results, "effluent1")
effluent2_bus = solph.views.node(results, "effluent2")
bio_methane_bus = solph.views.node(results, "bio-methane")


# plot the time series (sequences) of a specific component/bus
if plt is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    custom_storage["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
    )
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    electricity_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    heat_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
    )
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    digested_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
    )
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    effluent2_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
    )
    fig.subplots_adjust(top=0.8)
    plt.show()

# print the solver results
print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

# print the sums of the flows around the electricity bus
print("********* Main results *********")
print(electricity_bus["sequences"].sum(axis=0))
print(heat_bus["sequences"].sum(axis=0))
print(digested_bus["sequences"].sum(axis=0))
print(custom_storage["sequences"].sum(axis=0))
print(sludge_bus["sequences"].sum(axis=0))
print(slurry_bus["sequences"].sum(axis=0))
print(bio_gas_bus["sequences"].sum(axis=0))
print(effluent1_bus["sequences"].sum(axis=0))
print(effluent2_bus["sequences"].sum(axis=0))
print(bio_methane_bus["sequences"].sum(axis=0))