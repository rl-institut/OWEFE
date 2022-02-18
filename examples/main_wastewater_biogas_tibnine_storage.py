'************* Tibnine Wastewater Biogas Project ************'
'''
   General description
   ----------------------
   This is an example for a wastewater biogas system represented in OWEFE
   Note: 
   
   Timestep: hour
            Input: dewatered sludge [kg/h]
            # Biogas production [m3/h]
            # Methane CH4  1m3 CH4 = 34 MJ : 3.6 MJ ~ 1 khw (source: IRENA statistics 2016)
   
   Data                                      
   ------                              
   ww_biogas_tibnine_raw.csv                                      
                              
                                 
   Installation requirements                                      
   ---------------------------                              
   Follow documentation located in repository of OWEFE: README_Wastewater_biogas.md
                       
'''

__copyright__ = "oemof developer group"
__license__ = "GPLv3"

# *********************************************************************************************
# imports
# *********************************************************************************************

# Default logger of oemof

import csv
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

# changing cwd to use the function from the main file
os.chdir("../src/")
from src.specs.digester_CSTR import Digester
from digester_demand import HeatCalculation
from digester_demand import ElectricityCalculation

os.chdir("../examples/")

# *********************************************************************************************
# set up oemof.solph
# *********************************************************************************************

solver = "cbc"
debug = True  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 8760  # 24 hour * 365 days
solver_verbose = False  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_example.log",
    screen_level=logging.INFO,
    file_level=logging.DEBUG,
)
print(f'Number of time steps measured : {number_of_time_steps} hours')

logging.info("Initialize the energy system")
date_time_index = pd.date_range(
    "1/1/2020", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# *********************************************************************************************
# inputs
# *********************************************************************************************
# Read input data file
data = pd.read_csv(r"ww_biogas_tibnine_raw.csv")
# Units of raw data file: dewatered_sludge [kg/h], heat demand [kW],
# electricity demand [kW], water demand [m³/h], timestep: H


# *********************************************************************************************
# case study specific iWEFEs characteristics
# *********************************************************************************************
# Feedstock Characteristics
sludge_density = 997  # [kg/m³]
sludge_specific_gravity = 1.02
sludge_heat_capacity = 4200  # [# J/kg°C] heat capacity of dewatered sludge assumed to be same as water
dry_solid_concentration = 0.2
volatile_solid_concentration = 0.8
specific_gas_production = 1  # [m³/kg VS] specific biogas production per kg destroyed volatile solid
# source: Final year project, Beirut Arab University, 2021

# Digester Design Parameters
average_mass_flow =data["dewatered_sludge"].mean()  # [kg/h]
design_mass_flow = average_mass_flow  # [kg/h]
average_volumetric_flow = 24*average_mass_flow/(sludge_specific_gravity*sludge_density)  # [m³/d]

retention_time = 22  # [d]
volatile_solid_destruction_rate = 0.6175  # @ retention time of 22 days
temp_digester = 35  # Temperature inside the Digester
# source: Final year project, Beirut Arab University, 2021

# Digester Design
digester_design = Digester(retention_time, design_mass_flow, volatile_solid_destruction_rate, sludge_density,
                 sludge_specific_gravity, dry_solid_concentration, volatile_solid_concentration,
                 specific_gas_production)
diameter, volume, f_b_cf, surface_area_total, filled_up_volume, organic_loading_rate, design_volumetric_flow = digester_design.compute()


for i, r in data.iterrows():
    heat_demand = HeatCalculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                  temp_digester=temp_digester, surface_area=surface_area_total,
                                  heat_capacity=sludge_heat_capacity, om_flow=average_mass_flow)
    data.loc[i, "heat_demand_digester"] = heat_demand.compute()

data.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

for i, r in data.iterrows():
    electricity_demand_digester = ElectricityCalculation(om_flow=average_mass_flow, filled_up_volume=filled_up_volume)
    data.loc[i, "electricity_demand_digester"] = electricity_demand_digester.compute()

data.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

# Create electricity demand panda.Series in same time index as the oemof flows for plotting
demand_electricity = data["demand_electricity"].to_list()
electricity_demand = pd.Series(demand_electricity,
                              index=date_time_index, name="electricity demand WWTP")

# Create dewatered_sludge panda.Series in same time index as the oemof flows for plotting
dewatered_sludge_ls = data["dewatered_sludge"].to_list()
dewatered_sludge = pd.Series(dewatered_sludge_ls,
                              index=date_time_index, name="dewatered sludge")


# *********************************************************************************************
# Saving system design results in csv
# *********************************************************************************************

a_file = open("Digester_Dimension.csv", "w")
a_dict = {"Diameter [m]": f'{round(diameter, 2)}'}
b_dict = {"Total Volume of Digester [m³]": f'{round(volume, 2)}'}
c_dict = {"Organic Loading Rate [kgVS/m³d]": f'{round(organic_loading_rate, 3)}'}
d_dict = {"Feed to Biogas Conversion Factor[m³/kg]": f'{round(f_b_cf, 2)}'}
e_dict = {"Total Surface Area [m²]": f'{round(surface_area_total, 2)}'}
f_dict = {"Design Volumetric Flow [m³/d]": f'{design_volumetric_flow}'}
g_dict = {"Average Volumetric Flow [m³/d]": f'{average_volumetric_flow}'}

writer = csv.writer(a_file)
for key, value in a_dict.items():
    writer.writerow([key, value])

for key, value in b_dict.items():
    writer.writerow([key, value])

for key, value in c_dict.items():
    writer.writerow([key, value])

for key, value in d_dict.items():
    writer.writerow([key, value])

for key, value in e_dict.items():
    writer.writerow([key, value])

for key, value in f_dict.items():
    writer.writerow([key, value])

for key, value in g_dict.items():
    writer.writerow([key, value])

a_file.close()

# *********************************************************************************************
# define iWEFEs/Create oemof objects (bus, sink , source, transformer, ...)
# *********************************************************************************************
logging.info("Create oemof objects")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create sludge influent bus
bsld = solph.Bus(label="sludge")

# create electricity bus
bel = solph.Bus(label="electricity")

# create biogas bus
bbgas = solph.Bus(label="biogas")
bch4 = solph.Bus(label="bio-methane")

# create heat bus
bheat = solph.Bus(label="heat")

# adding the buses to the energy system
energysystem.add(bsld, bel, bbgas, bch4, bheat)

# create excess sink for the biogas bus to allow overproduction
energysystem.add(solph.Sink(label="excess_biogas", inputs={bch4: solph.Flow()}))

# create excess sink to represent electricity production
energysystem.add(solph.Sink(label="electricity production", inputs={bel: solph.Flow()}))

# create excess sink to represent heat production
energysystem.add(solph.Sink(label="excess heat production", inputs={bheat: solph.Flow()}))

# create fixed source object representing domestic sewage
energysystem.add(
    solph.Source(
        label="dewatered_sludge",
        outputs={bsld: solph.Flow(fix=data["dewatered_sludge"], nominal_value=1)},
    )
)

energysystem.add(
    solph.Sink(
        label="electricity demand digester",
        inputs={bel: solph.Flow(fix=data["electricity_demand_digester"], nominal_value=1)},
    )
)
# # create sink object representing the heat demand


energysystem.add(
    solph.Sink(
        label="heat demand digester",
        inputs={bheat: solph.Flow(fix=data["heat_demand_digester"], nominal_value=1)},
    )
)

# create dewatered sludge storage
storage = solph.components.GenericStorage(
    nominal_storage_capacity=1000000,
    label="dewatered sludge storage",
    inputs={bsld: solph.Flow()},
    outputs={bsld: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=None,
    inflow_conversion_factor=1,
    outflow_conversion_factor=1,
)

energysystem.add(storage)

energysystem.add(
    solph.Transformer(
        label="anaerobic digester",
        inputs={bsld: solph.Flow(nominal_value=average_mass_flow)},  # constant inflow for CSTR digester
        outputs={bbgas: solph.Flow()},
        conversion_factors={bbgas: f_b_cf},
    )
)

energysystem.add(
    solph.Transformer(
        label="biogas to methane conversion",
        inputs={bbgas: solph.Flow()},
        outputs={bch4: solph.Flow(nominal_value=10e5)},
        conversion_factors={bch4: 0.62*9.4},  # biogas to methane conversion factor: 0.62 (El Joauhari et al. 2021);
        # heat value of methane: 34 MJ/m³ -> 9.4 kWh/m³
    )
)

energysystem.add(
    solph.Transformer(
        label="CHP",
        inputs={bch4: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e5),
                 bheat: solph.Flow(nominal_value=10e5)},
        conversion_factors={bel: 0.9*0.35, bheat: 0.9*0.65},  # biogas boiler efficiency: 0.9 (BAU, 2021);
        # biogas engine efficiency 0.35 (BAU, 2021);
        # thermal conversion factor: 0.65
    )
)

##########################################################################
# Simulate the iWEFEs and plot the results
##########################################################################

logging.info("Simulate the iWEFEs")

# initialise the operational model
model = solph.Model(energysystem)

# This is for debugging only. It is not(!) necessary to solve the problem and
# should be set to False to save time and disc space in normal use. For
# debugging the timesteps should be set to 3, to increase the readability of
# the lp-file.
if debug:
    filename = os.path.join(
        solph.helpers.extend_basic_path("lp_files"), "ww_biogas_tibnine_proceed.lp"
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
storage = energysystem.groups["dewatered sludge storage"]

# *****************************************************************************
# get results of a specific node (component/bus)
# *****************************************************************************

electricity_bus = solph.views.node(results, "electricity")
heat_bus = solph.views.node(results, "heat")
sludge_bus = solph.views.node(results, "sludge")
biogas_bus = solph.views.node(results, "biogas")
bio_methane_bus = solph.views.node(results, "bio-methane")
storage_sequence_kg = results[(storage, None)]["sequences"]
# changing unit of storage sequence [kg -> m³]
storage_sequence_m3 = storage_sequence_kg * 1/(sludge_density*sludge_specific_gravity)

# ******************************************************************************
# Create further operation time series (sequences)
# ******************************************************************************
# Create electricity demand panda.Series in same time index as the oemof flows for plotting
demand_electricity = data["demand_electricity"].to_list()
electricity_demand = pd.Series(demand_electricity,
                              index=date_time_index, name="electricity demand WWTP")

# Create dewatered_sludge volumetric flow panda.Series in same time index as the oemof flows for plotting
dewatered_sludge_ls = data["dewatered_sludge"].to_list()
dewatered_sludge = pd.Series(dewatered_sludge_ls,
                              index=date_time_index, name="dewatered sludge")



if plt is not None:

    fig, ax = plt.subplots(figsize=(10,5))
    sludge_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post", ylim=[0, None]
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Dewatered Sludge Bus")
    plt.xlabel("Time Period")
    plt.ylabel("Mass Flow [kg/h]")
    plt.show()

    fig, ax = plt.subplots(figsize=(10,5))
    storage_sequence_m3.plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Dewatered Sludge Storage")
    plt.xlabel("Time Period")
    plt.ylabel("Storage Content [m³]")
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    biogas_bus["sequences"].plot(
    ax= ax, kind="line", drawstyle="steps-post", ylim=[0, 10]
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Biogas")
    plt.xlabel("Time Period [h]")
    plt.ylabel("Biogas Production [m³/h]")
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    electricity_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    electricity_demand.plot(
       ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Electricity Bus")
    plt.xlabel("Time Period [h]")
    plt.ylabel("Electrical Energy [kW]")
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    heat_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.3),
        ncol=3,
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Heat Bus")
    plt.xlabel("Time Period [h]")
    plt.ylabel("Heat [kW]")
    plt.show()

# ***************************************************************************
#  print and export the results
# ***************************************************************************
print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")
# create annual sums of the flows around the buses and saving the aggregated data in a csv file
print("********* Main results *********")
pp.pprint(energysystem.results["main"])

# calculate annual production sums and export them as csv file
sludge_sum = sludge_bus["sequences"].sum(axis=0)
# only Series and DataFrame objs are valid
biogas_sum = biogas_bus["sequences"].sum(axis=0)
electricity_sum = electricity_bus["sequences"].sum(axis=0)
heat_sum = heat_bus["sequences"].sum(axis=0)
# calculate minimum required storage capacity
storage_capacity_min = storage_sequence_m3.max(axis=0)


comb_sum = pd.concat([sludge_sum, biogas_sum, electricity_sum, heat_sum, storage_capacity_min], axis=0)
dfcomb = pd.DataFrame(comb_sum, columns=["Value"])
dfcomb.to_csv("main_results.csv", index=True)
dfcomb.info()
print(comb_sum)
print("----------")