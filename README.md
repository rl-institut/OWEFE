# OWEFE - open modeling framework for integrated water, energy, food, and environment systems

## Scientific Abstract
The integrated approach to managing the fundamental resources for human life, namely, water, energy, food, and the environment as their irreplaceable foundation, presents a profound opportunity for sustainable development. However, despite their huge potential, integrated water, energy, food, and environment systems (iWEFEs) are rarely put into practice because of, among others, complexity and a lack of uniform and openly available models to describe, configure and simulate such systems. To fill this gap, we present the open modeling framework for integrated water, energy, food, and environment systems (OWEFE) based on the open energy modeling framework (OEMOF). OWEFE follows an open, cross-sectoral, and modular design approach to address crucial challenges for the project development of iWEFEs.  The wide application of the framework can improve the assessment, planning, and configuration of iWEFEs for sustainable and integrated infrastructure development.

Please cite our publication when using OWEFE:

Fleischmann, J., Blechinger, P., Ribbe, L., Nauditt, A., El Achkar, J.H., Tiwari, K., Kuleape, R., Platzer, W., 2023. OWEFE - open modeling framework for integrated water, energy, food, and environment systems. Environmental Research: Infrastructure & Sustainability. [http://dx.doi.org/10.1088/2634-4505/acbcee](http://dx.doi.org/10.1088/2634-4505/acbcee)



___
## Installation

The currently supported Python Version is 3.8.10. For using OWEFE clone the repository to your local machine. Then create a new virtual environment with Python Version 3.8.10. Activate the new virtual environment and move to the repository folder to install the requirements of OWEFE.

     pip install -r requirements.txt
     pip install oemof.solph==0.4.4

Further, you need to install a solver in your system. For instruction on doing so please seeTo do so, please see the [oemof README](https://github.com/oemof/oemof-solph#readme). When installing a solver on a windows computer please note that the path variable must link to the folder where the solver.exe file (e.g., "cbc.exe") is located, not the solver.exe file itself.

## Get Started

For using OWEFE, check out the wastewater-biogas and agrivoltaics models in the example folders. You can adapt them acccording to your site conditions and create further model examples. Specfic components of the iWEFEs are stored in src/specs.

## Contribution

OWEFE is open for new models of environmental technologies. So if you like to contribute, we are available to support your project, answer your questions, investigate new issues and review pull requests.


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
