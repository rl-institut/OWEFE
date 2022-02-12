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
   
   Following integrated water energy system is modelled: 
   
                                    input/output    bsld  bbgas  bch4  bel  bheat  bslu  bdig  beff1  beff2      
                                        |           |      |      |    |     |      |     |     |      |
                                        |           |      |      |    |     |      |     |     |      |
     sewage(fixed source)               |---------->|      |      |    |     |      |     |     |      |       
                                        |           |      |      |    |     |      |     |     |      |
     digester_gas(Transformer)          |<----------|      |      |    |     |      |     |     |      |
                                        |----------------->|      |    |     |      |     |     |      |
                                        |           |      |      |    |     |      |     |     |      |
     digester_slu(Transformer)          |<----------|      |      |    |     |      |     |     |      |
                                        |------------------------------------------>|     |     |      |
                                        |           |      |      |    |     |      |     |     |      |                                 
     bio_methane(Transformer)           |<-----------------|      |    |     |      |     |     |      |      
                                        |------------------------>|    |     |      |     |     |      |     
                                        |           |      |      |    |     |      |     |     |      |
     CHP(Transformer)                   |<------------------------|    |     |      |     |     |      |     
                                        |----------------------------->|     |      |     |     |      |                   
                                        |----------------------------------->|      |     |     |      |     
                                        |           |      |      |    |     |      |     |     |      |
     dewatering_dig(Transformer)        |<------------------------------------------|     |     |      |     
                                        |------------------------------------------------>|     |      |    
                                        |           |      |      |    |     |      |     |     |      |                                 
     dewatering_eff(Transformer)        |<------------------------------------------|     |     |      |     
                                        |------------------------------------------------------>|      |                                    
                                        |           |      |      |    |     |      |     |     |      |
     constructed_wetland(Transformer)   |<------------------------------------------------------|      |                                  
                                        |------------------------------------------------------------->|    
                                        |           |      |      |    |     |      |     |     |      |                                 
     demand(electricity)(sink)          |<-----------------------------|     |      |     |     |      |     
                                        |           |      |      |    |     |      |     |     |      |                                 
     demand(heat)(sink)                 |<-----------------------------------|      |     |     |      |      
                                        |           |      |      |    |     |      |     |     |      |                                 
     demand(water)(sink)                |<-------------------------------------------------------------|     
                                        |           |      |      |    |     |      |     |     |      |                                 
     demand(fertilizer)(sink)           |<------------------------------------------------|     |      |    
                                        |           |      |      |    |     |      |     |     |      |                                 
     storage(Storage)                   |<------------------------|    |     |      |     |     |      |     
                                        |------------------------>|    |     |      |     |     |      |                                    


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
# ******************* PART 1 - Define the iWEFEs **********************************************
# *********************************************************************************************

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


# changing cwd to use the function from the main file
os.chdir("../src/")
from src.specs.digester_KT import Digester
from src.specs.constructedwetlands import Constructed_wetlands
from digester_demand import HeatCalculation
from digester_demand import ElectricityCalculation

os.chdir("../examples/")

# *********************************************************************************************
# inputs
# *********************************************************************************************
# Read input data file after
data = pd.read_csv(r"ww_biogas_tibnine_raw.csv")
# Units of raw data file: wastewater/dewatered_sludge [kg/h], heat demand [kWh/h],
# electricity demand [kWh/h], water demand [m³]

# *********************************************************************************************
# case study specific iWEFEs characteristics
# *********************************************************************************************
# Digester operation parameters
# temperature inside of the digester = 35 degree Celsius (source: final year project, 2021, Beirut Arab University)
retention_time = 22  # retention time set to 22 days (source: final year project, 2021, Beirut Arab University)
# Characteristic of input sludge
# incoming organic matter flow
design_mass_flowrate = data["wastewater"].max()  # [kg/h]
print(f'Mass flow rate {design_mass_flowrate}')
sludge_density = 997  # kg/m3 (source: final year project, 2021, Beirut Arab University)
sludge_specific_gravity = 1.02  # unitless, (source: final year project, 2021, Beirut Arab University)
heat_capacity_sludge = 4200  # J/kg°C heat capacity dewatered sludge assumed to be same as water
# (source: final year project, 2021, Beirut Arab University)
yield_factor = 9.3  # (source: final year project, 2021, Beirut Arab University)
# dry solid concentration = 20% of wet feedstock sludge (source: final year project, 2021, Beirut Arab University)
# volatile solid concentration = 80% of dry solid (source: final year project, 2021, Beirut Arab University)

digester_design = Digester(retention_time, design_mass_flowrate, sludge_density, sludge_specific_gravity, yield_factor)
diameter, volume, bg_prod, surface_area_total, filled_up_volume, organic_loading_rate, volumetric_flowrate = digester_design.compute()
print('surface_area_total: ', round(surface_area_total, 2))

for i, r in data.iterrows():
    heat_demand = HeatCalculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                  temp_digester=35, surface_area=surface_area_total,
                                  heat_capacity=heat_capacity_sludge, om_flow=design_mass_flowrate)
    data.loc[i, "heat_demand_digester"] = heat_demand.compute()

data.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

for i, r in data.iterrows():
    electricity_demand = ElectricityCalculation(om_flow=r['wastewater'], filled_up_volume=filled_up_volume)
    data.loc[i, "electricity_demand_digester"] = electricity_demand.compute()

data.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

solver = "cbc"
debug = True  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 24 * 365  # 24 hour * 365 days
solver_verbose = False  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_example.log",
    screen_level=logging.INFO,
    file_level=logging.DEBUG,
)
print(f'Number of time steps measured : {number_of_time_steps} hours')

# *********************************************************************************************
# setup an energy system
# *********************************************************************************************

logging.info("Initialize the energy system")
date_time_index = pd.date_range(
    "1/1/2021", periods=number_of_time_steps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)
# *********************************************************************************************
# Create oemof objects (bus, sink , source, transformer....)
# *********************************************************************************************
logging.info("Create oemof objects")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create sludge influent bus
bsld = solph.Bus(label="sludge")

# create electricity bus
bel = solph.Bus(label="electricity")

# create slurry bus
bslu = solph.Bus(label="slurry")

# create effluent bus
beff1 = solph.Bus(label="effluent1")
beff2 = solph.Bus(label="effluent2")

# create digestate bus
bdig = solph.Bus(label="digestate")

# create biogas bus
bbgas = solph.Bus(label="biogas")
bch4 = solph.Bus(label="bio-methane")

# create heat bus
bheat = solph.Bus(label="heat")

# adding the buses to the energy system
energysystem.add(bsld, bel, bslu, beff1, beff2, bdig, bbgas, bch4, bheat)

# create excess sink for the biogas bus to allow overproduction
energysystem.add(solph.Sink(label="excess_biogas", inputs={bch4: solph.Flow()}))

# create excess sink to represent electricity production
energysystem.add(solph.Sink(label="excess_electricity", inputs={bel: solph.Flow()}))

# create excess sink to represent heat production
energysystem.add(solph.Sink(label="excess_heat", inputs={bheat: solph.Flow()}))

# create excess sink to represent the water production
energysystem.add(solph.Sink(label="excess_water", inputs={beff2: solph.Flow()}))

# create sink object representing the fertilizer production
energysystem.add(solph.Sink(label="excess_fertilizer", inputs={bdig: solph.Flow()}))

# create fixed source object representing domestic sewage
energysystem.add(
    solph.Source(
        label="wastewater",
        outputs={bsld: solph.Flow(fix=data["wastewater"], nominal_value=1)},
    )
)

energysystem.add(
    solph.Sink(
        label="electricity_demand_digester (kWh)",
        inputs={bel: solph.Flow(fix=data["electricity_demand_digester"], nominal_value=1)},
    )
)
# # create sink object representing the heat demand


energysystem.add(
    solph.Sink(
        label="heat_demand_digester",
        inputs={bheat: solph.Flow(fix=data["heat_demand_digester"], nominal_value=1)},
    )
)

# *********************************************************************************************
# biogas production form the digester and saving results in csv
# *********************************************************************************************

digester_design = Digester(retention_time, design_mass_flowrate, sludge_density, sludge_specific_gravity, yield_factor)
design_diameter, volume, bg_conv_factor, surface_area_total, filled_up_volume, organic_loading_rate, volumetric_flowrate = digester_design.compute()
print(f'Total design diameter : {round(design_diameter, 2)} m')
print(f'Total volume of digester : {round(volume, 2)} m³')
print('biogas conversion factor: ', round(bg_conv_factor, 2))
print(f'surface_area_total: , {round(surface_area_total, 2)} m²')
print(f'Organic loading rate (OLR) : {round(organic_loading_rate, 2)} Kg VS/m3.days')
print(f'volumetric flowrate : {round(volumetric_flowrate, 2)} m3/hour')
a_file = open("Digester_Dimension.csv", "w")
a_dict = {"Total design diameter": f'{round(design_diameter, 2)} m'}
b_dict = {"Total volume of digester": f'{round(volume, 2)} m³'}
c_dict = {"Biogas conversion factor": f'{round(bg_conv_factor, 2)} '}
d_dict = {"surface_area_total": f'{round(surface_area_total, 2)} m²'}
e_dict = {"Volumetric flow rate": f'{volumetric_flowrate} m3/days'}
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
a_file.close()

# *********************************************************************************************
# exceptions to ensure viable digester efficiency
# *********************************************************************************************
# if bg_conv_factor < 0.3:
#     print(f'bg_prod_result {bg_conv_factor} is too low to proceed')
#     raise Exception
# elif bg_conv_factor > 1:
#     print(f'bg_prod_result {bg_conv_factor} is too large to proceed')
#     raise Exception

# create simple transformer object representing the biogas digester

energysystem.add(
    solph.Transformer(
        label="digester_gas",
        inputs={bsld: solph.Flow()},
        outputs={bbgas: solph.Flow(nominal_value=10e5)},
        conversion_factors={bbgas: bg_conv_factor},
    )
)

energysystem.add(
    solph.Transformer(
        label="digester_slurry",
        inputs={bsld: solph.Flow()},
        outputs={bslu: solph.Flow(nominal_value=10e5)},
        conversion_factors={bslu: 0.50},
    )
)
energysystem.add(
    solph.Transformer(
        label="bio_methane",
        inputs={bbgas: solph.Flow()},
        outputs={bch4: solph.Flow(nominal_value=10e5)},
        conversion_factors={bch4: 0.65*9.4},
    )
)


energysystem.add(
    solph.Transformer(
        label="CHP",
        inputs={bch4: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e5),
                 bheat: solph.Flow(nominal_value=10e5)},
        conversion_factors={bel: 0.35, bheat: 0.6},  # electrical conversion factor: 0.35;
        # thermal conversion factor: 0.6
    )
)

energysystem.add(
    solph.Transformer(
        label="dewatering_dig",
        inputs={bslu: solph.Flow()},
        outputs={bdig: solph.Flow(nominal_value=10e2)},
        conversion_factors={bdig: 0.42},
    )
)

energysystem.add(
    solph.Transformer(
        label="dewatering_eff",
        inputs={bslu: solph.Flow()},
        outputs={beff1: solph.Flow(nominal_value=10e2)},
        conversion_factors={beff1: 0.9},
    )
)

energysystem.add(
    solph.Transformer(
        label="constructed_wetland",
        inputs={beff1: solph.Flow()},
        outputs={beff2: solph.Flow(nominal_value=10e2)},
        conversion_factors={beff2: 0.9},
    )
)

# create storage object representing a biogas storage
storage = solph.components.GenericStorage(
    nominal_storage_capacity=10000,
    label="ch4_storage",
    inputs={bch4: solph.Flow()},
    outputs={bch4: solph.Flow(nominal_value=10000 / 6)},
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

# *****************************************************************************
# get all variables of a specific component/bus
# *****************************************************************************

custom_storage = solph.views.node(results, "ch4_storage")
electricity_bus = solph.views.node(results, "electricity")
heat_bus = solph.views.node(results, "heat")
digestate_bus = solph.views.node(results, "digestate")
sludge_bus = solph.views.node(results, "sludge")
slurry_bus = solph.views.node(results, "slurry")
biogas_bus = solph.views.node(results, "biogas")
effluent1_bus = solph.views.node(results, "effluent1")
effluent2_bus = solph.views.node(results, "effluent2")
bio_methane_bus = solph.views.node(results, "bio-methane")

# ******************************************************************************
# plot the time series (sequences) of a specific component/bus
# ******************************************************************************
if plt is not None:
    # fig, ax = plt.subplots(figsize=(10, 5))
    # custom_storage["sequences"].plot(
    #   ax=ax, kind="line", drawstyle="steps-post"
    # )
    # plt.legend(
    #     loc="upper center",
    #     prop={"size": 8},
    #     bbox_to_anchor=(0.5, 1.25),
    #     ncol=2,
    # )

    # fig.subplots_adjust(top=0.8)
    # plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    electricity_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8)
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
    fig.subplots_adjust(top=0.8)
    plt.title("Heat Bus")
    plt.xlabel("Time Period [h]")
    plt.ylabel("Heat [kW]")
    plt.show()
    #
    fig, ax = plt.subplots(figsize=(10, 5))
    digestate_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
    )
    fig.subplots_adjust(top=0.8)
    plt.title("Digestate Bus")
    plt.xlabel("Time Period [h]")
    plt.ylabel("Flow [m³]")
    plt.grid()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 3))
    effluent2_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="lower center",
        prop={"size": 8},
        bbox_to_anchor=(0.5, 1.25),
        ncol=1,
    )
    fig.subplots_adjust(top=0.7)
    plt.title("Effluent2 Bus")
    plt.xlabel("Time Period [hour]")
    plt.ylabel("Flow [m³]")
    plt.show()

# ***************************************************************************
#  print the solver results
# ***************************************************************************
print("********* Meta results *********")
pp.pprint(energysystem.results["meta"])
print("")

# create annual sums of the flows around the buses and saving the aggregated data in a csv file
print("********* Main results *********")
methane_series = bio_methane_bus["sequences"].sum(axis=0)
elec_series = electricity_bus["sequences"].sum(axis=0)
heat_series = heat_bus["sequences"].sum(axis=0)
storage_series = custom_storage["sequences"].sum(axis=0)
print("----------")


comb_series = pd.concat([methane_series, elec_series, heat_series, storage_series], axis=0)
dfcomb = pd.DataFrame(comb_series, columns=["Value"])
dfcomb.to_csv("main_results.csv", index=True)
print(comb_series)
print("----------")

# print(heat2_bus["sequences"].sum(axis=0))
print(digestate_bus["sequences"].sum(axis=0))
print(custom_storage["sequences"].sum(axis=0))
print(sludge_bus["sequences"].sum(axis=0))
print(slurry_bus["sequences"].sum(axis=0))
print(biogas_bus["sequences"].sum(axis=0))
print(effluent1_bus["sequences"].sum(axis=0))
print(effluent2_bus["sequences"].sum(axis=0))
print(bio_methane_bus["sequences"].sum(axis=0))

logging.info("************Average discharge (influent & effluent) in CW************")
print(effluent1_bus["sequences"].mean())
influ_array = effluent1_bus["sequences"].max().to_numpy()
influ_list1 = np.array(influ_array.tolist())
inflow = float(round(influ_list1[0], 2))

print(effluent2_bus["sequences"].mean())
influ_array = effluent2_bus["sequences"].max().to_numpy()
influ_list2 = np.array(influ_array.tolist())
outflow = float(round(influ_list2[0], 2))
# inflow1 = str(round(inflow, 2))
print(inflow)
print(outflow)

logging.info("*****Checking different parameters with WHO guidelines*******")
parameter = Constructed_wetlands(152, 137)
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
fig, axs = plt.subplots(1, 2, figsize=(5, 5))
axs[0].plot(bio_methane)
axs[0].set_title('bio_methane production')
axs[0].set_ylabel('bio_methane (KWh)')
axs[0].set_xlabel('time (hour)')
plt.show()
