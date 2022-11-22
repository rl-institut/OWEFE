# Create geometry & solar distribution to calculate shading factor using bifacial_radiance
# (inspired by Tutorial 11 - Advanced topics - AgriPV Systems,
# available online: https://github.com/NREL/bifacial_radiance/tree/main/docs/tutorials)

import os
import math
from pathlib import Path
try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')


testfolder = Path().resolve() / 'Geometry' / 'TEMP' / 'T1'

print("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
# Create a Radiance Object
demo = RadianceObj('T1', str(testfolder))

# Make Module

# Module Parameters
moduletype = 'APV_2_UP'
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
azimuth = 232.5  # in degrees
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
metdata = demo.readWeatherFile(epwfile, coerce_year=2018)
# Generate the Sky
demo.genCumSky()
# Combine ground, sky, and scene objects
octfile = demo.makeOct()

# demo.getfilelist()  # see what files got merged into the octfile
demo.getfilelist()

# Analyze and get Results

analysis = AnalysisObj(octfile, "on_module")
sensorsy = 16
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
results = analysis.analysis(octfile, "on_module", frontscan, backscan)

# Adding the structure -> simplification -> no structure

# Analyse Ground Irradiance

analysis = AnalysisObj(octfile, "ground")
sensorsy = 16
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)

groundscan = frontscan
groundscan['zstart'] = 0.05  # measurements 5 cm above the ground
groundscan['ystart'] = 0  # groundscan in center of APV plant below Modules (row 8)
groundscan['xstart'] = 0  # groundscan in center of APV plant below Modules (row 8)
#  Measurements along azimuth of APV Plant south/west direction
groundscan['zinc'] = 0   # height measurement remains constant
groundscan['yinc'] = -((math.cos(tilt)*(numpanels*y)+pitch*(nRows-1))/sensorsy)
groundscan['xinc'] = -((math.cos(tilt)*(numpanels*y)+pitch*(nRows-1))/sensorsy)

analysis.analysis(octfile, "ground", groundscan, backscan)

# Calculate Shading Factor
#os.chdir("/Geometry/TEMP/T1/EPWs")
#epw_irradiance_data = pd.read_csv(r"metdata_temp.csv")
#sum_irradiance_sky = epw_irradiance_data.sum(axis=0)
#os.chdir("../results")
#irr_ground=pd.read_csv("irr_ground.csv")
#sum_irradiance_ground=irr_ground("Wm2Front")
#shading_factor = sum_irradiance_ground/sum_irradiance_sky
#os.chdir("../../../../")