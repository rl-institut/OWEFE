# OWEFE - Example 1 : Tebnine Wastewater Treatment and Biogas model

## What's here

* We use the data produced by students from [Beirut Arab University](https://www.bau.edu.lb) for the town Tebnine, Lebanon. 
* If you want to see the code with better readability, refer to [this branch](https://github.com/rl-institut/OWEFE/tree/Kapil)

**Summary**
> The domestic sewage carried into the Anaerobic digester [Floating drum digester](https://energypedia.info/wiki/Floating_Drum_Biogas_Plants) by the truck. The digester consist of the propeller for mixing with a sludge retention time of 22 days. Methane gas which is in the range of 55 - 65% of bio-gas [Source](https://www.researchgate.net/publication/264416846_Development_of_Biogas_Combustion_in_Combined_Heat_and_Power_Generation) is also considered during modelling of the energy system. Methane gas is burned in combined heat & power plant(CHP), that enhance is the source of heat and electricity. Part of the heat and electricity is supplied to the digester itself to maintain the heat loss and to power the propeller respectively. [Slurry](https://en.wikipedia.org/wiki/Slurry#:~:text=A%20slurry%20is%20a%20mixture,up%20to%20hundreds%20of%20millimeters.) is taken into consideration through [dewatering unit](https://www.hcr-llc.com/blog/what-is-sludge-dewatering) where water is allowed to pass through [constructed wetlands](https://sswm.info/taxonomy/term/3933/horizontal-subsurface-flow-constructed-wetland) and remained [digestate](https://en.wikipedia.org/wiki/Digestate) can be further used as fertilizer. The energy model analyze the operational parameters like; [Biochemical oxygen demand (BOD)]( https://en.wikipedia.org/wiki/Biochemical_oxygen_demand), [Chemical oxygen demand (COD)](https://en.wikipedia.org/wiki/Chemical_oxygen_demand), Nitrate, [pathogens](https://en.wikipedia.org/wiki/Escherichia_coli). 

### 📚 Removal of hydrogen Sulphide (H2S)

* Desulphurization (letting the biogas to pass through the iron tube to react with) [source](https://www.researchgate.net/publication/278024272_Removal_of_Hydrogen_Sulfide_H2S_from_Biogas_Using_Zero-Valent_Iron).
* Absorption into a liquid either water or caustic solution (might cause the wastewater problem if not treated well) [source](https://www.researchgate.net/publication/222814070_Biogas_Scrubbing_Compression_and_Storage_Perspective_and_Prospectus_in_Indian_Context).
* Biological conversion by which sulfur compounds are converted into elemental sulfur by sulfide oxidizing microorganisms with addition of air/oxygen (might lead to explosive in the range of 6 – 12% CH4 in the presence of O2 [source](https://www.semanticscholar.org/paper/Removal-of-Hydrogen-Sulfide-from-Biogas-Using-Zicari-Graf/f233ab85e32a7c22bdf0887d2b5be0a76b796f1c).
* Activated carbon.

### 📚 Removal of Carbon dioxide (CO2)

* water scrubbing (example; by using iron wool)
* Membrane systems
* Pressure swing adsorption (PSA) 
* Chemical CO2 absorption
* Amine gas treatment
* CO2 by cooling and recovering dry ice.

## Flow Chart of Energy Model

![Biogas:wastewater_CFD](https://github.com/rl-institut/OWEFE/blob/master/docs/assets/flowchart.png)

## Components to the energy system

* Sink (one input, no output)
* Source (one output, no input)
* Linear Transformer (one input, n outputs)
* Storage (one input, one output)

### BUS

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

### [Sink]((https://oemof-solph.readthedocs.io/en/latest/usage.html#sink-basic))

Sink is normally used to define the demand within an energy model, but it can also be used to detect excesses. Following names were used to define SINK.
* Demand 1 (water)
* Demand 2 (fertilizer)
* Demand 3 (electricity)
* Demand 4 (Heat)
In contrast to the demand sink, ‘excess sink’ has normally less restrictions but is opened to take the whole excess.

### [Source](https://oemof-solph.readthedocs.io/en/latest/usage.html#source-basic)

The model can be represented by only one source, ‘Domestic Sewage’, where it might be restricted by maximum value (nominal_value), annual limit (Summed_max), cost for importing the sewage (Variable_cost). The nominal_value sets the installed capacity. 

### [Linear Transformer](https://oemof-solph.readthedocs.io/en/latest/usage.html#transformer-basic]

LinearTransformer in the model represents the transforming process of given input to output. Following names were used to define Lineartransformer.
* Anaerobic digester
* Dewatering Unit
* Constructed wetland (CW)
* Combined heat & power plant (CHP)

