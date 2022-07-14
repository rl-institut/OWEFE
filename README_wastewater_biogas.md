# OWEFE - Example 1 : Tebnine Wastewater Treatment and Biogas model

## What's here ?

* We use the data produced by students from [Beirut Arab University](https://www.bau.edu.lb) for the town Tebnine, Lebanon. 
* If you want to see the code with better readability, refer to [this branch](https://github.com/rl-institut/OWEFE/tree/Kapil)

## Summary
> The domestic sewage carried into the Anaerobic digester [Floating drum digester](https://energypedia.info/wiki/Floating_Drum_Biogas_Plants) by the truck. The digester consist of the propeller for mixing with a sludge retention time of 22 days. Methane gas which is in the range of 55 - 65% of bio-gas [[reference]](https://www.researchgate.net/publication/264416846_Development_of_Biogas_Combustion_in_Combined_Heat_and_Power_Generation) is also considered during modelling of the energy system. Methane gas is burned in a combined heat & power plant(CHP). Part of the heat and electricity is supplied to the digester itself to maintain the heat loss and to power the propeller respectively. The major part of electricity produced is used to power the wastewater treatment plant. [Slurry](https://en.wikipedia.org/wiki/Slurry#:~:text=A%20slurry%20is%20a%20mixture,up%20to%20hundreds%20of%20millimeters.) is taken into consideration through [dewatering unit](https://www.hcr-llc.com/blog/what-is-sludge-dewatering) where water is allowed to pass through [constructed wetlands](https://sswm.info/taxonomy/term/3933/horizontal-subsurface-flow-constructed-wetland) and remained [digestate](https://en.wikipedia.org/wiki/Digestate) can be further used as fertilizer. The model analyze the operational parameters like; [Biochemical oxygen demand (BOD)]( https://en.wikipedia.org/wiki/Biochemical_oxygen_demand), [Chemical oxygen demand (COD)](https://en.wikipedia.org/wiki/Chemical_oxygen_demand), Nitrate, [pathogens](https://en.wikipedia.org/wiki/Escherichia_coli). 


## Flowchart

![flowchart_wastewater_biogas](https://github.com/rl-institut/OWEFE/blob/master/docs/assets/flowchart_wastewater_biogas.png)

## Elements

* Bus
* FLow
* Sink (one input, no output)
* Source (one output, no input)
* Linear Transformer (one input, n outputs)
* Storage (one input, one output)

### Bus

All flows into and out of a bus are balanced. Following names were used to define BUS. 
* Sludge (m3/day)
* Slurry (m3/day)
* Effluent (m3/day)
* Electricity (Kwh)
* Biogas (m3/day)
* Bio-methane (m3/day)
* Heat (Kwh)

### Flow

The flow class has to be used to connect. An instance of the Flow class is normally used in combination with the definition of a component. 

### [Sink](https://oemof-solph.readthedocs.io/en/latest/usage.html#sink-basic)

Sink is normally used to define the demand within the model, but it can also be used to detect excesses. Following names were used to define the sinks of the iWEFEs.
* Demand 1 (water)
* Demand 2 (fertilizer)
* Demand 3 (electricity)
* Demand 4 (Heat)

In contrast to the demand sink, ‘excess sink’ has normally less restrictions but is opened to take the whole excess.

### [Source](https://oemof-solph.readthedocs.io/en/latest/usage.html#source-basic)

The model can be represented by only one source, ‘Domestic Sewage’, where it might be restricted by maximum value (nominal_value), annual limit (Summed_max), cost for importing the sewage (Variable_cost). The nominal_value sets the installed capacity. 

### [Linear Transformer](https://oemof-solph.readthedocs.io/en/latest/usage.html#transformer-basic)

LinearTransformer in the model represents the transforming process of given input to output. Following system elements were modelled as linear transformers:
* Anaerobic digester
* Dewatering Unit
* Constructed wetland (CW)
* Combined heat & power plant (CHP)

## Get Statrted

### Install
The currently supported Python Version is 3.8.10. For using OWEFE clone the repository to your local machine. Then create a new virtual environment with Python Version 3.8.10. Activate the new virtual environment and move to the repository folder.

    `pip install -r requirements`

Further, you need to intall a solver in your system. To do so, please see the oemof README: 
[oemof README](https://github.com/oemof/oemof-solph#readme)

### Data Preparation 
We assume you already have the following data named [ww_biogas_tibnine_raw.csv](https://github.com/rl-institut/OWEFE/blob/master/examples/ww_biogas_tibnine_raw.csv)

### Steps keep into consideration before run the main file 

* [main_wastewater_biogas_tibnine.py](https://github.com/rl-institut/OWEFE/blob/master/examples/main_wastewater_biogas_tibnine.py) calls [pre_design_wastewater_biogas.py](https://github.com/rl-institut/OWEFE/blob/master/examples/pre_design_wastewater_biogas.py)

        import pre_design_wastewater_biogas
 
* [pre_design_wastewater_biogas.py](https://github.com/rl-institut/OWEFE/blob/master/examples/pre_design_wastewater_biogas.py) calls [digester_demand.py](https://github.com/rl-institut/OWEFE/blob/master/examples/digester_demand.py) for heat and electricity demand for digester. 
 
        from digester_demand import heat_calculation
        from digester_demand import electricity_calculation
 
*   [pre_design_wastewater_biogas.py](https://github.com/rl-institut/OWEFE/blob/master/examples/pre_design_wastewater_biogas.py) again calls [digester.py](https://github.com/rl-institut/OWEFE/blob/master/examples/components/digester.py) to calculate bio-gas production per feed and dimension of digester. 

        from components.digester import Digester
 
*   [pre_design_wastewater_biogas.py](https://github.com/rl-institut/OWEFE/blob/master/examples/pre_design_wastewater_biogas.py) produce a new csv file named under [proceed.csv] and it will automatically saved in your local repository.
 
        for i, r in inpdf.iterrows():
            heat_demand = heat_calculation(temp_ambient=r['temperature'], heat_transfer_coefficient=0.6,
                                    temp_digester=35, surface_area_total_overground= area)
            inpdf.loc[i, "heat_demand_digester"] = heat_demand.compute()

        inpdf.to_csv("ww_biogas_tibnine_proceed.csv", index=False)

        for i, r in inpdf.iterrows():
            electricity_demand = electricity_calculation(wastewater=r['wastewater'])
            inpdf.loc[i, "electricity_demand_digester"] = electricity_demand.compute()

        inpdf.to_csv("ww_biogas_tibnine_proceed.csv", index=False)
 
 * Read the new Proceed csv file
 
        pd.read_csv(r"ww_biogas_tibnine_proceed.csv")
 
 * [main_wastewater_biogas_tibnine.py](https://github.com/rl-institut/OWEFE/blob/master/examples/main_wastewater_biogas_tibnine.py) calls [constructedwetlands.py](constructedwetlands.py). This will produce average discharge from constructed wetlands, area required for wetlands, BOD effluent, COD effluent and Nitrate effluent.
 
        from components.constructedwetlands import Constructed_wetlands
 
 ## Result
 
### Sum of the flows following various buses can be calculated from the wastewater biogas model: 

     electricity_bus["sequences"].sum(axis=0)
     heat_bus["sequences"].sum(axis=0)
     digested_bus["sequences"].sum(axis=0)
     custom_storage["sequences"].sum(axis=0)
     sludge_bus["sequences"].sum(axis=0)
     slurry_bus["sequences"].sum(axis=0)
     bio_gas_bus["sequences"].sum(axis=0)
     effluent1_bus["sequences"].sum(axis=0)
     effluent2_bus["sequences"].sum(axis=0)
     bio_methane_bus["sequences"].sum(axis=0)

### Checking different parameters with WHO guidelines

     Constructed_wetlands(inflow, outflow)

### Graph Plotting

A line graph for electricity demand, heat demand, water demand, fertilizer demand and bio-methane gas production is plotted against time period. For example; 

    fig, ax = plt.subplots(figsize=(10, 5))
    electricity_bus["sequences"].plot(
        ax=ax, kind="line", drawstyle="steps-post"
    )
    plt.legend(
        loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2
    )
    fig.subplots_adjust(top=0.8)
    plt.show()

## Contact

Feel free to create a issue or contact us if there are any questions [Julian Fleischmann](julian.fleischmann@rl-institute.de) or [Kapil Tiwari](Kapil.Tiwari@rl-institut.de).

If there are any issues involving running/using OWEFE, make sure to open an issue, it would be greatly appreciated, and will help improve the project.

## Additional Notes

Functions have been designed with flexibility in mind, so that full customization of built-in-functions and filters can be utilised; for every buses differing graph with demand and supply can be created; just by changing parameters slightly, demand sink can be convert into excess sink.

Planners & developers who would like to work with renewable energy and environmental technolohies can use the present tool to model biogas wastewater systems including usability of methane gas for combined heat and power generation, water filtration under WHO guideliness, and usage of digestate as fertilizer. This library provides a complete suite of functions to do so, as well as in-built filters and presets.

## Contributing

OWEFE is always open for modeling further technologies and functionalities. So if you'd like to contribute, we're always ready to investigate and develop new models coperativley.

## To Do

*  Fix Constructed wetlands 
*  Fix slurry flow (currently 0), digestate and effluent 2 graph
*  Simplify Sludge to Methane Conversion (omit Biogas Bus and Methane storage),
*   change methane bus unit from kWh (chemical energy content) to m³
*  add dewatered_sludge_sum to output results.csv, main_wastewater_tibnine, line 558

## Contributors

* [Kapil Tiwari](Kapil.Tiwari@rl-institut.de)
* [Julian Fleischmann](julian.fleischmann@rl-institute.de) 

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](https://github.com/rl-institut/OWEFE/blob/master/LICENSE) file for details.
