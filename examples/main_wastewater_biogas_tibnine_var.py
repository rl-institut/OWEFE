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
# import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# changing cwd to use the function from the main file
os.chdir("../src/")
from src.specs.digester_floating_drum import Digester
#  from src.components.constructedwetlands import Constructed_wetlands
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
# electricity demand [kW], water demand [m??/h], timestep: H


# *********************************************************************************************
# case study specific iWEFEs characteristics
# *********************************************************************************************
# Feedstock Characteristics
sludge_density = 997  # [kg/m??]
sludge_specific_gravity = 1.02
sludge_heat_capacity = 4200  # [# J/kg??C] heat capacity of dewatered sludge assumed to be same as water
dry_solid_concentration = 0.2
volatile_solid_concentration = 0.8
specific_gas_production = 1  # [m??/kg VS] specific biogas production per kg destroyed volatile solid
# source: Final year project, Beirut Arab University, 2021

# Digester Design Parameters
design_mass_flow = data["dewatered_sludge"].max()  # [kg/h]
average_mass_flow =data["dewatered_sludge"].mean()  # [kg/h]
average_volumetric_flow = 24*average_mass_flow/(sludge_specific_gravity*sludge_density)  # [m??/d]

retention_time = 22  # [d]
volatile_solid_destruction_rate = 0.6175  # @ retention time of 22 days
temp_digester = 35  # Temperature inside the Digester
# source: Final year project, Beirut Arab University, 2021

# Digester Design
digester_design = Digester(retention_time, design_mass_flow, volatile_solid_destruction_rate, sludge_density,
                 sludge_specific_gravity, dry_solid_concentration, volatile_solid_concentration,
                 specific_gas_production)
diameter, volume, f_b_cf, surface_area_total, filled_up_volume, organic_loading_rate, volumetric_flowrate = digester_design.compute()
print('surface_area_total: ', round(surface_area_total, 2))

for i, r in data.iterrows():
    heat_demand = HeatCalculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                  temp_digester=temp_digester, surface_area=surface_area_total,
                                  heat_capacity=sludge_heat_capacity, om_flow=r['dewatered_sludge'])
    data.loc[i, "heat_demand_digester"] = heat_demand.compute()

data.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

for i, r in data.iterrows():
    electricity_demand_digester = ElectricityCalculation(om_flow=r['dewatered_sludge'], filled_up_volume=filled_up_volume)
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
# define iWEFEs/Create oemof objects (bus, sink , source, transformer, ...)
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
energysystem.add(solph.Sink(label="electricity production", inputs={bel: solph.Flow()}))

# create excess sink to represent heat production
energysystem.add(solph.Sink(label="excess heat production", inputs={bheat: solph.Flow()}))

# create excess sink to represent the water production
energysystem.add(solph.Sink(label="water production", inputs={beff2: solph.Flow()}))

# create sink object representing the fertilizer production
energysystem.add(solph.Sink(label="fertilizer production", inputs={bdig: solph.Flow()}))

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

# *********************************************************************************************
# biogas production form the digester and saving results in csv
# *********************************************************************************************

digester_design = Digester(retention_time, design_mass_flow, volatile_solid_destruction_rate, sludge_density,
                 sludge_specific_gravity, dry_solid_concentration, volatile_solid_concentration,
                 specific_gas_production)
design_diameter, volume, biogas_prod, surface_area_total, filled_up_volume, organic_loading_rate, design_volumetric_flow = digester_design.compute()
print(f'Diameter [m] : {round(design_diameter, 2)} ')
print(f'Total volume of digester [m??] : {round(volume, 2)}')
print(f'feedstock to biogas conversion factor [kg -> m??]: {round(f_b_cf, 2)}')
print(f'Total Surface Area: , {round(surface_area_total, 2)}')
print(f'Organic loading rate (OLR) : {round(organic_loading_rate, 2)} [Kg VS/(m??d)]')
print(f'Volumetric Flow Rate : {round(design_volumetric_flow, 2)} [m3/h]')
a_file = open("Digester_Dimension.csv", "w")
a_dict = {"Diameter [m]": f'{round(design_diameter, 2)}'}
b_dict = {"Total Volume of Digester [m??]": f'{round(volume, 2)}'}
c_dict = {"Feed to Biogas Conversion Factor[m??/kg]": f'{round(f_b_cf, 2)}'}
d_dict = {"Total Surface Area [m??]": f'{round(surface_area_total, 2)}'}
e_dict = {"Design Volumetric Flow [m??/d]": f'{design_volumetric_flow}'}
f_dict = {"Average Volumetric Flow [m??/d]": f'{average_volumetric_flow}'}
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
        conversion_factors={bbgas: f_b_cf},
    )
)

energysystem.add(
    solph.Transformer(
        label="slurry output of digester",
        inputs={bsld: solph.Flow()},
        outputs={bslu: solph.Flow(nominal_value=10e5)},
        conversion_factors={bslu: 0.50},
    )
)

energysystem.add(
    solph.Transformer(
        label="bio-methane bus",
        inputs={bbgas: solph.Flow()},
        outputs={bch4: solph.Flow(nominal_value=10e5)},
        conversion_factors={bch4: 0.62*9.4},  # biogas to methane conversion factor: 0.62 (El Joauhari et al. 2021);
        # heat value of methane: 34 MJ/m?? -> 9.4 kWh/m??
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

energysystem.add(
    solph.Transformer(
        label="dewatering unit",
        inputs={bslu: solph.Flow()},
        outputs={bdig: solph.Flow(nominal_value=10e2)},
        conversion_factors={bdig: 0.42},
    )
)

energysystem.add(
    solph.Transformer(
        label="dewatering eff",
        inputs={bslu: solph.Flow()},
        outputs={beff1: solph.Flow(nominal_value=10e2)},
        conversion_factors={beff1: 0.9},
    )
)

energysystem.add(
    solph.Transformer(
        label="constructed wetland",
        inputs={beff1: solph.Flow()},
        outputs={beff2: solph.Flow(nominal_value=10e2)},
        conversion_factors={beff2: 0.9},
    )
)

# create storage object representing a biogas storage
storage = solph.components.GenericStorage(
    nominal_storage_capacity=10000,
    label="CH4 storage",
    inputs={bch4: solph.Flow()},
    outputs={bch4: solph.Flow(nominal_value=10000 / 6)},
    loss_rate=0.00,
    initial_storage_level=None,
    inflow_conversion_factor=1,
    outflow_conversion_factor=0.8,
)

energysystem.add(storage)

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
storage = energysystem.groups["CH4 storage"]

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
# get results of a specific component/bus
# *****************************************************************************


custom_storage = solph.views.node(results, "CH4 storage")
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
# plot the time series (sequences) of specific components
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
    dewatered_sludge.plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Dewatered Sludge")
    plt.xlabel("Time Period")
    plt.ylabel("Mass Flow [kg/h]")
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    biogas_bus["sequences"].plot(
    ax= ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8, bottom=0.15)
    plt.title("Biogas")
    plt.xlabel("Time Period [h]")
    plt.ylabel("Biogas Production [m??/h]")
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
dewatered_sludge_sum = dewatered_sludge.sum()  #  cannot concatenate object of class numpy.float64,
# only Series and DataFrame objs are valid
biogas_sum = biogas_bus["sequences"].sum(axis=0)
electricity_sum = electricity_bus["sequences"].sum(axis=0)
heat_sum = heat_bus["sequences"].sum(axis=0)
#storage_series = custom_storage["sequences"].sum(axis=0)

type(dewatered_sludge)
type(dewatered_sludge_sum)
comb_sum = pd.concat([biogas_sum, electricity_sum, heat_sum], axis=0)
dfcomb = pd.DataFrame(comb_sum, columns=["Value"])
dfcomb.to_csv("main_results.csv", index=True)
print(comb_sum)
print("----------")

# print(heat2_bus["sequences"].sum(axis=0))
# print(digestate_bus["sequences"].sum(axis=0))
# print(custom_storage["sequences"].sum(axis=0))
# print(sludge_bus["sequences"].sum(axis=0))
# print(slurry_bus["sequences"].sum(axis=0))
# print(biogas_bus["sequences"].sum(axis=0))
# print(effluent1_bus["sequences"].sum(axis=0))
# print(effluent2_bus["sequences"].sum(axis=0))
# print(bio_methane_bus["sequences"].sum(axis=0))

# logging.info("************Average discharge (influent & effluent) in CW************")
# print(effluent1_bus["sequences"].mean())
# influ_array = effluent1_bus["sequences"].max().to_numpy()
# influ_list1 = np.array(influ_array.tolist())
# inflow = float(round(influ_list1[0], 2))

# print(effluent2_bus["sequences"].mean())
# influ_array = effluent2_bus["sequences"].max().to_numpy()
# influ_list2 = np.array(influ_array.tolist())
# outflow = float(round(influ_list2[0], 2))
# inflow1 = str(round(inflow, 2))
# print(inflow)
# print(outflow)

# logging.info("*****Checking different parameters with WHO guidelines*******")
# parameter = Constructed_wetlands(152, 137)
# avg_discharge, cw_area, net_evaporation, BOD_effluent, COD_effluent, NO3_effluent = parameter.compute()
# print('BOD5 effluent : ', round(BOD_effluent, 2))
# print('COD effluent : ', round(COD_effluent, 2))
# print('Nitrate effluent: ', round(NO3_effluent, 2))


# Biogas Production_single graph: sequences_is pd DataFrame -> make to pd.Series should work!
# bio_methane_bus_npy = bio_methane_bus["sequences"].to_numpy()
# print(bio_methane_bus_npy)
# bio_methane = bio_methane_bus_npy[:, 2]
# fig, ax = plt.subplots(figsize=(10, 5))
# bio_methane.plot(
#    ax=ax, kind="line", drawstyle = "steps-post"
#)
#plt.legend(
#    loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
#)
#fig.subplots_adjust(top=0.8, bottom=0.15)
#plt.title('Bio Methane production')
#plt.xlabel('Time Period [h]')
#plt.ylabel('Energy Content bio-methane [kW]')
#plt.show()



