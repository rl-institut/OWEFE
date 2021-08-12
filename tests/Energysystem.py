# Default logger of oemof
from oemof.tools import logger
from oemof import solph

import logging
import os
import pandas as pd
import pprint as pp


try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# define logger
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

# setup an energy system
logging.info("Initialize the energy system")
date_time_index = pd.date_range(
    "1/1/2021", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# Read data file
#filename = os.path.join(os.getcwd(), "basic_example_copy.csv")
data = pd.read_csv(r"C:\Users\t2_ka\Desktop\Sample Test Oemof 2\basic_example_copy.csv")

# Create oemof objects bus, sink , source, transformer...

logging.info("Create oemof objects")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create influent bus
bsld = solph.Bus(label="sludge")

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

# create heat bus
bheat = solph.Bus(label="heat")

# adding the buses to the energy system
energysystem.add(bsld, bel, bslu, beff1, beff2, bdig, bbgas, bheat)

# create excess component for the bio-gas bus to allow overproduction
energysystem.add(solph.Sink(label="excess_bio-gas", inputs={bbgas: solph.Flow()}))

# create fixed source object representing domestic sewage
energysystem.add(
    solph.Source(
        label="wastewater",
        outputs={bsld: solph.Flow(fix=data["wastewater"], nominal_value=100000)},
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

# total volume of the digester m3, initial concentration of volatile solid in slurry kg/m3, yield factor
# area = 8
# height = 5
# conc = 200
# y_factor = 1
# bg_production = Biogas(area, height, conc, y_factor)
# biogas_production = bg_production.compute()
# print(biogas_production)

# # create simple transformer object representing a gas power plant
# energysystem.add(
#     solph.Transformer(
#         label="digester",
#         inputs={bsld: solph.Flow()},
#         outputs={bbgas: solph.Flow(nominal_value=10e5, variable_costs= 0.0001),
#                   bslu: solph.Flow(nominal_value=10e6, variable_costs= 0.0001)},
#         conversion_factors={bbgas: 0.50,bslu: 0.5},
#     )
# )
#
# energysystem.add(
#     solph.Transformer(
#         label="CHP",
#         inputs={bbgas: solph.Flow()},
#         outputs={bel: solph.Flow(nominal_value=10e5, variable_costs= 0.0001),
#                 bheat: solph.Flow(nominal_value=10e4, variable_costs = 0.0001)},
#         conversion_factors={bel: 0.58, bheat: 0.70},
#     )
# )
#
# energysystem.add(
#     solph.Transformer(
#         label="dewatering",
#         inputs={bslu: solph.Flow()},
#         outputs={bdig: solph.Flow(nominal_value=10e2, variable_costs = 0.0001),
#                 beff1: solph.Flow(nominal_value=10e3, variable_costs = 0.0001)},
#         conversion_factors={bdig: 0.42, beff1: 0.30},
#     )
# )
#
# energysystem.add(
#     solph.Transformer(
#         label="cw",
#         inputs={beff1: solph.Flow()},
#         outputs={beff2: solph.Flow(nominal_value=10e2, variable_costs = 0.0001)},
#         conversion_factors={beff2: 0.6},
#     )
# )
#
# # create storage object representing a battery
# storage = solph.components.GenericStorage(
#     nominal_storage_capacity=10077997,
#     label="ch4_storage",
#     inputs={bbgas: solph.Flow(nominal_value=10077997 / 6)},
#     outputs={bbgas: solph.Flow(nominal_value=10077997 / 6,
#              variable_costs=0.001)},
#     loss_rate=0.00,
#     initial_storage_level=None,
#     inflow_conversion_factor=1,
#     outflow_conversion_factor=0.8,
# )
#
# energysystem.add(storage)

# create simple transformer object representing a gas power plant
energysystem.add(
    solph.Transformer(
        label="digester_gas",
        inputs={bsld: solph.Flow()},
        outputs={bbgas: solph.Flow(nominal_value=10e5, variable_costs=50)},
        conversion_factors={bbgas: 0.58},
    )
)

energysystem.add(
    solph.Transformer(
        label="CHP_el",
        inputs={bbgas: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e5, variable_costs=50)},
        conversion_factors={bel: 0.58},
    )
)

energysystem.add(
    solph.Transformer(
        label="CHP_th",
        inputs={bbgas: solph.Flow()},
        outputs={bheat: solph.Flow(nominal_value=10e4, variable_costs=70)},
        conversion_factors={bheat: 0.70},
    )
)
energysystem.add(
    solph.Transformer(
        label="digester_slu",
        inputs={bsld: solph.Flow()},
        outputs={bslu: solph.Flow(nominal_value=10e4, variable_costs=60)},
        conversion_factors={bslu: 0.42},
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
        outputs={beff2: solph.Flow(nominal_value=10e2, variable_costs=50)},
        conversion_factors={beff2: 0.6},
    )
)

# create storage object representing a battery
storage = solph.components.GenericStorage(
    nominal_storage_capacity=10077997,
    label="ch4_storage",
    inputs={bbgas: solph.Flow()},
    outputs={bbgas: solph.Flow(nominal_value=10077997 / 6)},
    loss_rate=0.00,
    initial_storage_level= None,
    inflow_conversion_factor=1,
    outflow_conversion_factor=0.8,
)

energysystem.add(storage)

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
digested_bus = solph.views.node(results, "digested")

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

# print the solver results
print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

# print the sums of the flows around the electricity bus
print("********* Main results *********")
print(electricity_bus["sequences"].sum(axis=0))
print(digested_bus["sequences"].sum(axis=0))
print(custom_storage["sequences"].sum(axis=0))