# OWEFE - open modeling framework for integrated water, energy, food, and eco- systems

## Scientific Abstract
Climate change and the unfettered consumption of resources threaten the very existence of humankind and the ecosystems that sustain life. In this context, the holistic approach to managing water, energy, and food presents a profound opportunity to tap synergies, minimize trade-offs across sectors and tackle the challenges. However, despite its potential, integrated Water, Eco-, Energy, Food systems (iWEFEs) are hardly put into practice due to, among others, a lack of generic and openly available models of iWEFEs, including their components, processes, flows, and cross-sectoral interconnections. To fill this gap, we present an open modeling framework for integrated Water, Energy, Food, and Eco-Systems (OWEFE). OWEFE is based on the open energy modeling framework (OEMOF) and conceptualized, addressing the current challenges of WEFE frameworks and the multiple characteristics of iWEFEs. OWEFE is calibrated and verified by two variants of iWEFEs -- agrivoltaics and renewable energy production through anaerobic digestion of wastewater -- including respective case study design and operational data. The verified framework enables the development of an open, research-community-driven database to provide technical, economic, and environmental models for preliminary assessment, synergistic planning, and software-based configuration of iWEFEs.


# rli_template
This repository is based on rli-template, a template repository for creating new projects under the RLI's umbrella

## Get started

Simply click on the green `Use this template` button on the left of the `Clone or download` button.

The detailed instructions to create a new repository from this template can be found [here](https://help.github.com/en/articles/creating-a-repository-from-a-template).

## src folder

This folder is where you should place the code of your package (package name to be edited in `setup.py` under name)

You can install it locally for developing with

    python setup.py install
    
More details for packaging are available on [https://packaging.python.org](https://packaging.python.org/tutorials/packaging-projects/)


## Docs

To build the docs simply go to the `docs` folder

    cd docs

Install the requirements

    pip install -r docs_requirements.txt

and run

    make html

The output will then be located in `docs/_build/html` and can be opened with your favorite browser

## Code linting

In this template, 3 possible linters are proposed:
- flake8 only sends warnings and error about linting (PEP8)
- pylint sends warnings and error about linting (PEP8) and also allows warning about imports order
- black sends warning but can also fix the files for you

You can perfectly use the 3 of them or subset, at your preference. Don't forget to edit `.travis.yml` if you want to deactivate the automatic testing of some linters!
