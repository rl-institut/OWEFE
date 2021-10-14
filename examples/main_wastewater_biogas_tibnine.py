# Default logger of oemof
# function: digester and constructed wetlands are inside src>> components
import csv
import math
import urllib.request
from oemof.tools import logger
from oemof import solph

# url = "https://raw.githubusercontent.com/rl-institut/OWEFE/master/src/components/digester.py"
# url_2 = "https://raw.githubusercontent.com/rl-institut/OWEFE/master/src/components/constructedwetlands.py"
# url_3 = "https://raw.githubusercontent.com/rl-institut/OWEFE/master/src/pre_design_wastewater_biogas.py"
# url_4 = "https://raw.githubusercontent.com/rl-institut/OWEFE/master/src/digester_demand.py"
#
# urllib.request.urlretrieve(url, 'digester.py')
# urllib.request.urlretrieve(url_2, 'constructedwetlands.py')
# urllib.request.urlretrieve(url_3, 'pre_design_wastewater_biogas.py')
# urllib.request.urlretrieve(url_4, 'digester_demand.py')

from components.digester import Digester
from components.constructedwetlands import Constructed_wetlands

import logging
import os
import pandas as pd
import pprint as pp
import numpy as np
import pre_design_wastewater_biogas

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

# setup an energy system
logging.info("Initialize the energy system")
date_time_index = pd.date_range(
    "1/1/2021", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# Read data file after running pre-design
data = pd.read_csv(r"ww_biogas_tibnine_proceed.csv")
design_flow = data["wastewater"].max()
print(f'design flow {design_flow}')

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
energysystem.add(solph.Sink(label="excess_bio-gas", inputs={bch4: solph.Flow()}))

# create excess component for the electricity bus to allow overproduction
energysystem.add(solph.Sink(label="excess_electricity", inputs={bel: solph.Flow()}))

# create excess component for the heat bus to allow overproduction
energysystem.add(solph.Sink(label="excess_heat", inputs={bheat: solph.Flow()}))

# create fixed source object representing domestic sewage
energysystem.add(
    solph.Source(
        label="wastewater",
        outputs={bsld: solph.Flow(fix=data["wastewater"], nominal_value=1000)},
    )
)

# # create sink object representing the electrical production
# energysystem.add(
#     solph.Sink(
#         label="demand_el",
#         inputs={bel: solph.Flow(fix=data["demand_el"], nominal_value=1)},
#     )
# )

energysystem.add(
    solph.Sink(
        label="electricity_demand_digester",
        inputs={bel: solph.Flow(fix=data["electricity_demand_digester"], nominal_value=1)},
    )
)
# # create sink object representing the thermal demand
# energysystem.add(
#     solph.Sink(
#         label="demand_th",
#         inputs={bheat: solph.Flow(fix=data["demand_th"], nominal_value=1)},
#     )
# )

energysystem.add(
    solph.Sink(
        label="heat_demand_digester",
        inputs={bheat: solph.Flow(fix=data["heat_demand_digester"], nominal_value=1)},
    )
)

# create sink object representing the water production
energysystem.add(
    solph.Sink(
        label="demand_water",
        inputs={beff2: solph.Flow(fix=data["demand_water"], nominal_value=1)},
    )
)

# create sink object representing the fertilizer production (-> excess)
energysystem.add(
    solph.Sink(
        label="demand_f",
        inputs={bdig: solph.Flow(fix=data["demand_f"], nominal_value=1)},
    )
)

# bio-gas production form the digester
retention_time = 22
bg_prod = Digester(retention_time, design_flow)
design_diameter, volume, bg_prod_result, surface_area_total_overground = bg_prod.compute()
print(f'Total design diameter : {round(design_diameter, 2)} meter')
print(f'Total volume of digester : {round(volume, 2)} m3')
print('biogas conversion factor: ', round(bg_prod_result, 2))
# exceptions to ensure viable digester efficiency
if bg_prod_result < 0.3:
    print(f'bg_prod_result {bg_prod_result} is too low to proceed')
    raise Exception
elif bg_prod_result > 1:
    print(f'bg_prod_result {bg_prod_result} is too large to proceed')
    raise Exception

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
        conversion_factors={bel: 0.5},
    )
)

# energysystem.add(
#     solph.Transformer(
#         label="CHP_el_digester",
#         inputs={bch4: solph.Flow()},
#         outputs={bel: solph.Flow(nominal_value=10e5, variable_costs=60)},
#         conversion_factors={bel: 3.2},
#     )
# )

energysystem.add(
    solph.Transformer(
        label="CHP_th",
        inputs={bch4: solph.Flow()},
        outputs={bheat: solph.Flow(nominal_value=10e5, variable_costs=60)},
        conversion_factors={bheat: 0.65},
    )
)

# energysystem.add(
#     solph.Transformer(
#         label="CHP_th_digester",
#         inputs={bch4: solph.Flow()},
#         outputs={bheat: solph.Flow(nominal_value=10e5, variable_costs=60)},
#         conversion_factors={bheat: 0.60},
#     )
# )

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
        conversion_factors={beff1: 0.9},
    )
)

energysystem.add(
    solph.Transformer(
        label="cw",
        inputs={beff1: solph.Flow()},
        outputs={beff2: solph.Flow(nominal_value=10e2, variable_costs=60)},
        conversion_factors={beff2: 0.9},
    )
)

# mean= solph.views.node(outputs, "effluent2")

# create storage object representing a biogas storage
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
# electricity2_bus = solph.views.node(results, "electricity2")
heat_bus = solph.views.node(results, "heat")
# heat2_bus = solph.views.node(results, "heat2")
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
    #
    #     fig, ax = plt.subplots(figsize=(10, 5))
    #     electricity2_bus["sequences"].plot(
    #         ax=ax, kind="line", drawstyle="steps-post"
    #     )
    #     plt.legend(
    #         loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    #     )
    #     fig.subplots_adjust(top=0.8)
    #     plt.show()
    #
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
#
#     heat2_bus["sequences"].plot(
#         ax=ax, kind="line", drawstyle="steps-post"
#     )
#     plt.legend(
#         loc="upper center",
#         prop={"size": 8},
#         bbox_to_anchor=(0.5, 1.25),
#         ncol=2,
#     )
#     fig.subplots_adjust(top=0.8)
#     plt.show()
#
#     fig, ax = plt.subplots(figsize=(10, 5))
#     digested_bus["sequences"].plot(
#         ax=ax, kind="line", drawstyle="steps-post"
#     )
#     plt.legend(
#         loc="upper center",
#         prop={"size": 8},
#         bbox_to_anchor=(0.5, 1.25),
#         ncol=2,
#     )
#     fig.subplots_adjust(top=0.8)
#     plt.show()
#
#     fig, ax = plt.subplots(figsize=(10, 5))
#     effluent2_bus["sequences"].plot(
#         ax=ax, kind="line", drawstyle="steps-post"
#     )
#     plt.legend(
#         loc="upper center",
#         prop={"size": 8},
#         bbox_to_anchor=(0.5, 1.25),
#         ncol=2,
#     )
#     fig.subplots_adjust(top=0.8)
#     plt.show()

#  print the solver results
print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

# print the sums of the flows around the electricity bus
print("********* Main results *********")
print(electricity_bus["sequences"].sum(axis=0))
# print(electricity2_bus["sequences"].sum(axis=0))
print(heat_bus["sequences"].sum(axis=0))
# print(heat2_bus["sequences"].sum(axis=0))
print(digested_bus["sequences"].sum(axis=0))
print(custom_storage["sequences"].sum(axis=0))
print(sludge_bus["sequences"].sum(axis=0))
print(slurry_bus["sequences"].sum(axis=0))
print(bio_gas_bus["sequences"].sum(axis=0))
print(effluent1_bus["sequences"].sum(axis=0))
print(effluent2_bus["sequences"].sum(axis=0))
print(bio_methane_bus["sequences"].sum(axis=0))

logging.info("************Average discharge (influent & effluent) in CW************")
print(effluent1_bus["sequences"].mean())
influ_array = effluent1_bus["sequences"].mean().to_numpy()
influ_list1 = np.array(influ_array.tolist())
inflow = float(round(influ_list1[0], 2))

print(effluent2_bus["sequences"].mean())
influ_array = effluent2_bus["sequences"].mean().to_numpy()
influ_list2 = np.array(influ_array.tolist())
outflow = float(round(influ_list2[0], 2))
# inflow1 = str(round(inflow, 2))
print(inflow)
print(outflow)

logging.info("*****Checking different parameters with WHO guidelines*******")
parameter = Constructed_wetlands(inflow, outflow)
avg_discharge, cw_area, net_evaporation, BOD_effluent, COD_effluent, NO3_effluent = parameter.compute()
print('BOD5 effluent : ', round(BOD_effluent, 2))
print('COD effluent : ', round(COD_effluent, 2))
print('Nitrate effluent: ', round(NO3_effluent, 2))

logging.info("***********Bio-gas utilization graph***************")
# print(len(bio_methane_bus["sequences"]))
print(bio_methane_bus["sequences"])

bio_methane_bus_npy = bio_methane_bus["sequences"].to_numpy()
print(bio_methane_bus_npy)
bio_methane = bio_methane_bus_npy[:, 0]
# CHP_el = bio_methane_bus_npy[:, 1]
# CHP_el_digester = bio_methane_bus_npy[:, 2]
# CHP_th = bio_methane_bus_npy[:, 3]
# CHP_th_digester = bio_methane_bus_npy[:, 4]
# ch4_storage_input = bio_methane_bus_npy[:, 5]
# ch4_storage_output = bio_methane_bus_npy[:, 6]
#
fig, axs = plt.subplots(1, 2, figsize=(5, 5))
axs[0].plot(bio_methane)
axs[0].set_title('bio_methane production')
axs[0].set_ylabel('bio_methane')
axs[0].set_xlabel('time')
#
# axs[1].plot(CHP_el)
# axs[1].set_title('ch4 el flow')
# axs[1].set_ylabel('CHP_el')
# axs[1].set_xlabel('time')
#
# axs[2].plot(CHP_el_digester)
# axs[2].set_title('Electricity into digester')
# axs[2].set_ylabel('CHP_el_digester')
# axs[2].set_xlabel('time')
#
# axs[3].plot(CHP_th)
# axs[3].set_title('ch4 th flow')
# axs[3].set_ylabel('CHP_th')
# axs[3].set_xlabel('time')
#
# axs[4].plot(CHP_th_digester)
# axs[4].set_title('Heat into digester')
# axs[4].set_ylabel('CHP_th_digester')
# axs[4].set_xlabel('time')
#
# axs[5].plot(ch4_storage_input)
# axs[5].set_title('ch4 input in a storage')
# axs[5].set_ylabel('ch4_storage_input')
# axs[5].set_xlabel('time')
#
# axs[6].plot(ch4_storage_output)
# axs[6].set_title('ch4 output from a storage')
# axs[6].set_ylabel('ch4_storage_output')
# axs[6].set_xlabel('time')
plt.show()
