# Basic Agrivoltaics Model (Version 0.2) - Case Study of Hegelbach
import math

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
os.chdir("../../src")

import src.specs.plant as plant
import src.specs.photovoltaic_panel as photovoltaic_panel

os.chdir("../examples/APV Hegelbach")


# *********************************************************************************************
# set up oemof.solph
# *********************************************************************************************

solver = "cbc"
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 8760
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
# time series for latitude = 47.9, longitude = 9.1
data = pd.read_csv(r"apv_hegelbach_raw.csv")
apv_temp = pd.read_csv(r"t_air_below_apv_calibrated_2018.csv")
climate_df = pd.read_csv(r"ERA5_pvlib_2018.csv")

et_o = 5  # take it out when real data is there, just for testing
vwc = 0.21  # see above et_o

# resample apv_temp for daily maximum temperature series
list_apv_temp = apv_temp["t_air"].values.tolist()
index = pd.date_range('1/1/2018', periods=8760, freq='H')
apv_temp_df = pd.DataFrame(data=list_apv_temp, index=index, columns=['t_air'])
apv_temp_D_max = apv_temp_df.resample('D').apply(lambda x : max(x))
apv_temp_D_max.to_csv("apv_temp_daily_max.csv", index=True)
apv_temp_D_max_H = apv_temp_D_max.resample('H').pad()
# apv_temp_D_max_list = apv_temp_D_max_H.values.tolist()
#  t_air_below_pv = pd.DataFrame(calibrated_data, columns=["Value"])
apv_temp_D_max_H.to_csv("apv_temp_daily_max_H.csv", index=True)

# *********************************************************************************************
# Component Characteristics
# *********************************************************************************************

# Solar Energy System Characteristics

# module_name = "SolarWorld SW 270 duo bifacial PV" Source: Schindele et al. 2020
# module_area = 1206 [m²], Source: Schindele et al. 2020
p_rpv = 270  # [Wp]
r_ref = 1000  # [W/m²]
n_t = -0.0037  # [1/°C], Value Source: Maleki et al. (2015), Ismail et al. (2013)
t_c_ref = 25  # [°C]
noct = 48  # [°C]
n_pv = 720  # amount of pv modules
# Inverter
# inverter_type/name: Huawei, SUN2000-36KTL; efficiency: 0.986; 0.9 is chosen to also cover further losses
inverter_efficiency = 0.9

# Plant characteristics

# Wheat Batten
light_saturation_point = 60000  # [lux]
# Cultivar parameters, source: simple crop model
t_sum = 2150
HI = 0.34
I50A = 280
I50B = 50
# Species Parameters
t_base = 0  # base temperature for phenological development and growth
t_opt = 15  # optimal temperature for biomass growth
RUE = 1.24  # Radiation Use efficiency (above ground only and without respiration) (g/MJm²)
I50maxH = 100
I50maxW = 25
t_heat = 34  # t_heat is the threshold temperature when biomass growth rate starts to be reduced by heat stress
t_ext = 45  # t_extreme is the extreme temperature threshold when the biomass growth rate reaches 0 due to heat stress
s_CO2 = 0.08
s_water = 0.4
rzd = 1000  # root zone depth [mm]
# cultivation area
area = 2000  # [m²]

# *********************************************************************************************
# Create Geometry
# *********************************************************************************************
# lacks automation !, calling APV_geometry from main file shall be implemented in future versions.
# Currently, we just have looked up the values for APV_geometry in the csv result files
shading_factor = 836447.4/1195402  # input [Wh/m²a],output: dimensionless
# ground irradiance average value of 9 measurements
# going from center of APV outward in azimuth direction
back_front_ratio = 0.126485
bifacial_factor = 1+back_front_ratio  # radiance ratio on bifacial module 1 (front) + back to front ratio
# W/m2 Front: 1207246; ->  1207 kWh/m²yr;
# in comparison; era5 ghi on horizontal plane
annual_ghi = climate_df["ghi"].sum()/1000
print("annual ghi [kWh/m²]")
print(annual_ghi)
# yes läuft, D ~ 1000 kWh/yr; horizontale Fläche; Neigung + Süden bringt bisschen mehr


# *********************************************************************************************
# define iWEFEs/Create oemof objects (bus, sink , source, transformer....)
# *********************************************************************************************
logging.info("Create OWEFE elements")
logging.info("Create iWEFEs elements")

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

# create solar energy bus on module
bsem = solph.Bus(label="solar energy bus module")

# create solar energy bus on ground
bseg = solph.Bus(label="solar energy bus ground")

# create plant internal bus 1
bp1 = solph.Bus(label="plant internal bus 1")

# create plant internal bus 2
bp2 = solph.Bus(label="plant internal bus 2")

# create DC electricity bus
bedc = solph.Bus(label="DC electricity bus")

# create AC electricity bus
beac = solph.Bus(label="AC electricity bus")

# create Biomass Bus
bb = solph.Bus(label="biomass bus")

# add buses to the iWEFEs
energysystem.add(bsem, bseg, bp1, bp2, bedc, beac, bb)

# Resources

# solar radiation from the sun
energysystem.add(
    solph.Source(
        label="Sun_module",
        outputs={bsem: solph.Flow(fix=climate_df["ghi"], nominal_value=bifacial_factor)})),

# irradiance on ground
energysystem.add(
    solph.Source(
        label="Sun_ground",
        outputs={bseg: solph.Flow(fix=climate_df["ghi"], nominal_value=shading_factor)})),

# Photovoltaic Panels
pv_te = photovoltaic_panel.calc_pv_te(
    t_air=apv_temp["t_air"], ghi=climate_df["ghi"], p_rpv=p_rpv, r_ref=r_ref, n_t=n_t, t_c_ref=t_c_ref, noct=noct)
energysystem.add(
    solph.Transformer(
        label="Photovoltaic Panels",
        inputs={bsem: solph.Flow()},
        outputs={bedc: solph.Flow()},
        conversion_factors={bedc: pv_te*n_pv},
    )
)

# Inverter
energysystem.add(
    solph.Transformer(
        label="Inverter",
        inputs={bedc: solph.Flow()},
        outputs={beac: solph.Flow()},
        conversion_factors={beac: inverter_efficiency},
    )
)

# Plant
# we have subdivided the plant in various sub-transformers
# to model the various environmental impacts on the plant's biomass production rate
# Transformer P1: Temperature and RUE impact on biomass growth rate

ti = plant.calc_te(t_air=apv_temp["t_air"], t_opt=t_opt, t_base=t_base, RUE=RUE)
energysystem.add(
    solph.Transformer(
        label="Plant_ti",
        inputs={bseg: solph.Flow()},
        conversion_factors={bp1: ti},
        outputs={bp1: solph.Flow()},
    )
)

# Transformer P2: Heat effect on biomass growth rate
hi = plant.calc_hi(t_max=apv_temp_D_max_H["t_air"], t_heat=t_heat, t_ext=t_ext)
energysystem.add(
    solph.Transformer(
        label="Plant_hi",
        inputs={bp1: solph.Flow()},
        conversion_factors={bp2: hi},
        outputs={bp2: solph.Flow()},
    )
)


# Transformer P3: Aridity impact on biomass growth rate
arid = plant.calc_arid(et_o=et_o, vwc=vwc, rzd=rzd)
energysystem.add(
    solph.Transformer(
        label="Plant_arid",
        inputs={bp2: solph.Flow()},
        conversion_factors={bb: arid},
        outputs={bb: solph.Flow()},
    )
)

# Sinks
# grid
energysystem.add(solph.Sink(label="grid", inputs={beac: solph.Flow()}))

# biomass harvest
energysystem.add(solph.Sink(label="harvest", inputs={bb: solph.Flow()}))


##########################################################################
# Simulate the iWEFEs and plot the results
##########################################################################

logging.info("Optimise the energy system")

# initialise the operational model
model = solph.Model(energysystem)

# This is for debugging only. It is not(!) necessary to solve the problem and
# should be set to false to save time and disc space in normal use. For
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
electricity_bus = solph.views.node(results, "AC electricity bus")
solar_bus_module = solph.views.node(results, "solar energy bus module")
solar_bus_ground = solph.views.node(results, "solar energy bus ground")
biomass_bus = solph.views.node(results, "biomass bus")

# ****************************************************************************
# Saving electricity and biomass production results in csv
# ****************************************************************************
# calculate annual production sums and export them as csv file
electricity_production = electricity_bus["sequences"].sum(axis=0)
biomass_production = biomass_bus["sequences"].sum(axis=0)
biomass_growth_period = biomass_bus["sequences"].loc["2018-01-01 00:00:00":"2018-07-31 12:00:00", :]
biomass_harvest = biomass_growth_period.sum(axis=0) * HI

comb_sum = pd.concat([electricity_production, biomass_production, biomass_harvest], axis=0)
dfcomb = pd.DataFrame(comb_sum, columns=["Value"])
dfcomb.to_csv("production.csv", index=True)
dfcomb.info()
print(comb_sum)

# ***************************************************************************
#  print the results
# ***************************************************************************

print("********* Meta results *********")
# pp.pprint(energysystem.results["meta"])
print("")

print("********* Main results *********")
# pp.pprint(energysystem.results["main"])

print("-----------")
# print(electricity_bus["sequences"].sum(axis=0))
# print(type(electricity_bus["sequences"].sum(axis=0).to_numpy()))
# print(electricity_bus["sequences"].sum(axis=0).to_numpy())
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
plt.title("Biomass Rate")
plt.xlabel("Time Period [h]")
plt.ylabel("[g/(h*m²)]")
plt.show()