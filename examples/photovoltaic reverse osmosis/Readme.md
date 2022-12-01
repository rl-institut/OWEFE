# OWEFE - Example 3 : Photovoltaic Reverse Osmosis Sytstem

The photovoltaic reverse osmosis system model is currently under development and not yet operative.

## What's here?

## Summary

## iWEFEs topology

![iWEFEs topology](https://github.com/rl-institut/OWEFE/blob/master/docs/assets/iWEFEs_topology_PV_RO.png)

## Elements

* Bus
* Flow
* Sink (one input, no output)
* Source (one output, no input)
* Linear Transformer (one input, n outputs)
* Storage (one input, one output)

## Required Inputs for system configuration
RO: 
System capacity (i.e. daily water demand) – Decides the element diameter
Feed water TDS – decides the type of the element to be used (BWRO, SWRO)
Foulants in the feed water (i.e. organic foulants, bivalent ions, silica or any other colloidal matters) – decides type of the element (for ex. fouling resistance) and pretreatment
Permeate quality and energy supply – decides recovery rate, high rejection elements, low pressure elements, etc.
input definition inspired by ‘RO-NF-FilmTec-Manual-45-D01504-en’ from DuPont
 
## Get Stared

### Install 
The currently supported Python Version is 3.8.10. For using OWEFE clone the repository to your local machine. Then create a new virtual environment with Python Version 3.8.10. Activate the new virtual environment and move to the repository folder.

    pip install -r requirements

Further, you need to intall a solver in your system. To do so, please see the [oemof README](https://github.com/oemof/oemof-solph#readme)

## Results

## Contributing

OWEFE is always open for modeling further technologies and functionalities. So if you'd like to contribute, we're always ready to investigate and develop new models coperativley.

## Contributors

* Vinay Narayan Hegde - vinay.narayan.hegde@ise.fraunhofer.de 
* Julian Fleischmann - julian.fleischmann@rl-institute.de


## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](https://github.com/rl-institut/OWEFE/blob/master/LICENSE) file for details.
