# -*- coding: utf-8

"""
This module provides functions to simulate the growth of plants.
This file is part of the project OWEFE;
It is inspired by oemof thermal, in detail by following module:
oemof-thermal/src/oemof/thermal/compression_heatpumps_and_chillers.py
(SPDX-License-Identifier of source module: MIT)
"""

import pandas as pd

def calc_te(t_air, t_opt, t_base, RUE):

    r"""
    Calculates the temperature on the biomass rate
    ----
    Parameters
    ----------
    t_air: ambient temperature as pd.series or list
    t_opt: optimum temperature for biomass growth
    t_base: base temperature for biomass growth
    RUE: Radiation use efficiency (above ground only and without respiration
    c_wh_to_mj: conversion factor Watt Hours (WH) to Mega Joules (MJ)
    Returns
    -------
    te : list of numerical values:
         temperature coefficients for calculating biomass rate

    """
    # Introduce conversion factor Watt Hours (WH) to Mega Joules (MJ)
    c_wh_to_mj = 3.6*10**(-3)
    # Check if input arguments have proper type and length
    if not isinstance(t_air, (list, pd.Series)):
        raise TypeError("Argument 'temp' is not of type list or pd.Series!")
    te = []    # creating a list
    # Calculate te
    for t in t_air:
        if t < t_base:
            x = 0
            te.append(x)

        elif t_base <= t <= t_opt:
            x = (t-t_base)/(t_opt-t_base) * RUE * c_wh_to_mj
            te.append(x)

        elif t > t_opt:
            x = 1 * RUE * c_wh_to_mj
            te.append(x)
    return te

def calc_arid(et_o, vwc, s_water, rzd):

    r"""
    Calculates the soil water availability impact on the biomass rate
    arid factor derived from simple crop model and Woli et al. (2012), divided by 24 to transform to hourly values
    ----
    Parameters
    ----------
    et_o: potential evapotranspiration
    vwc: volumetric water content
    rzd: root zone depth

    Returns
    -------
    arid : list of numerical values:
         aridity factor affecting the biomass rate

    """

    # Check if input arguments have proper type and length
    if not isinstance(et_o, (list, pd.Series)):
        raise TypeError("Argument 'et_o' is not of type list or pd.Series!")
    wi = []    # creating a list
    # Calculate arid

    for e in et_o:
        for m in vwc:
            wi = 1-s_water*(1 - min(abs(e), (0.096/24)*m*rzd)/abs(e))
    return wi

def calc_hi(t_max, t_heat, t_ext):

    r"""
    Calculates the heat impact on the biomass rate
    ----
    Parameters
    ----------
    t_max: daily maximum temperature as pd.series or list
    t_ext: optimum temperature for biomass growth
    t_heat: threshold temperature when biomass growth rate starts to be reduced by heat stress

    Returns
    -------
    hi : list of numerical values:
         temperature coefficients for calculating biomass rate

    """
    # Check if input arguments have proper type and length
    if not isinstance(t_max, (list, pd.Series)):
        raise TypeError("Argument t_max is not of type list or pd.Series!")
    hi = []    # creating a list
    # Calculate te
    for t in t_max:
        if t <= t_heat:
            x = 1
            hi.append(x)

        elif t_heat < t <= t_ext:
            x = (t-t_heat)/(t_ext-t_heat)
            hi.append(x)

        elif t > t_ext:
            x = 0
            hi.append(x)

    return hi

