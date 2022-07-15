# OWEFE - Example 2 : Agrivoltaics in Hegelbach

## What's here?

## Summary

## Flowchart

![flowchart_agrivoltaics](https://github.com/rl-institut/OWEFE/blob/master/docs/assets/flowchart_agrivoltaics_0.1.png)

## Elements

* Bus
* Flow
* Sink (one input, no output)
* Source (one output, no input)
* Linear Transformer (one input, n outputs)
* Storage (one input, one output)

## Get Stared

### Install 
The currently supported Python Version is 3.8.10. For using OWEFE clone the repository to your local machine. Then create a new virtual environment with Python Version 3.8.10. Activate the new virtual environment and move to the repository folder.

    `pip install -r requirements`

Further, you need to intall a solver in your system. To do so, please see the [oemof README](https://github.com/oemof/oemof-solph#readme)

For Agrivoltaics systems we use the bifacial_radiance package to model the distribution of solar irradiance on the plants. Therefore bifacial_radiance has to be installed on the computer. To do so, please follow [bifacial_radiance README](https://github.com/NREL/bifacial_radiance/blob/main/README.md)
## Results

## Contributing

OWEFE is always open for modeling further technologies and functionalities. So if you'd like to contribute, we're always ready to investigate and develop new models coperativley.

## Contributors

* [Julian Fleischmann](julian.fleischmann@rl-institute.de) 

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](https://github.com/rl-institut/OWEFE/blob/master/LICENSE) file for details.
