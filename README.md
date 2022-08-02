# OWEFE - open modeling framework for integrated water, energy, food, and environment systems

## Scientific Abstract
Climate change and the unfettered consumption of resources threaten the very existence of humankind and the ecosystems that sustain life. In this context, the holistic approach to managing water, energy, and food presents a profound opportunity to tap synergies, minimize trade-offs across sectors and tackle the challenges. However, despite its potential, integrated Water, Eco-, Energy, Food systems (iWEFEs) are hardly put into practice due to, among others, a lack of generic and open available models of iWEFEs, including their components, processes, flows, and cross-sectoral interconnections. To fill this gap, we present an open modeling framework for integrated Water, Energy, Food, and environment systems (OWEFE). OWEFE is based on the open energy modeling framework (OEMOF) and conceptualized, addressing the current challenges of WEFE frameworks and the multiple characteristics of iWEFEs. OWEFE is calibrated and verified by two variants of iWEFEs -- agrivoltaics and renewable energy production through anaerobic digestion of wastewater -- including respective case study design and operational data. The verified framework enables the development of an open, research-community-driven database to provide technical, economic, and environmental models for preliminary assessment, synergistic planning, and software-based configuration of iWEFEs.

___
## Installation

The currently supported Python Version is 3.8.10. For using OWEFE clone the repository to your local machine. Then create a new virtual environment with Python Version 3.8.10. Activate the new virtual environment and move to the repository folder to install the requirements of OWEFE.

     pip install -r requirements.txt
     pip install oemof.solph=0.4.4

Further, you need to intall a solver in your system. To do so, please see the [oemof README](https://github.com/oemof/oemof-solph#readme)

## Get Started

For using OWEFE, check out the wastewater-biogas and agrivoltaics models in the example folders. You can adapt them acccording to your site conditions and create further model examples. Specfic components of the iWEFEs are stored in src/specs.

## Contribution

OWEFE is open for new functions and models of environmental technologies. So if you'd like to contribute, we're always ready to answer your questions, investigate new issues and review pull requests.


## Documentation

Documentation is currenty done in README files. For seeing how the wastewater-biogas model and the agrivoltaics model work, please check their READMEs in the main directory. In a next step, we build up a readthedocs in the `docs` folder.

## Code linting

In this template, 3 possible linters are proposed:
- flake8 only sends warnings and error about linting (PEP8)
- pylint sends warnings and error about linting (PEP8) and also allows warning about imports order
- black sends warning but can also fix the files for you

You can perfectly use the 3 of them or subset, at your preference. Don't forget to edit `.travis.yml` if you want to deactivate the automatic testing of some linters!

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](https://github.com/rl-institut/OWEFE/blob/master/LICENSE) file for details.

# rli_template

This repository is based on rli-template, a template repository for creating new projects under the RLI's umbrella
