# -*- coding: utf-8

"""
This module provides functions to simulate the growth of plants.
This file is part of the project OWEFE;
It is inspired by oemof thermal, in detail by following module:
oemof-thermal/src/oemof/thermal/compression_heatpumps_and_chillers.py
(SPDX-License-Identifier of source module: MIT)
"""

import pandas as pd
def calc_ei(t_air, t_opt, t_base, RUE):

    r"""
    Calculates the environmental impact on the biomass rate
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
    ei = []    # creating a list
    # Calculate te
    for t in t_air:
        if t < t_base:
            x = 0
            ei.append(x)

        elif t_base <= t <= t_opt:
            x = (t-t_base)/(t_opt-t_base)*RUE*c_wh_to_mj
            ei.append(x)

        elif t > t_opt:
            x = 1*RUE*c_wh_to_mj
            ei.append(x)

    return ei
