# -*- coding: utf-8

"""
This module provides functions to simulate the growth of plants.
This file is part of the project OWEFE;
It is inspired by oemof thermal, in detail by following module:
oemof-thermal/src/oemof/thermal/compression_heatpumps_and_chillers.py
(SPDX-License-Identifier of source module: MIT)
"""

import pandas as pd
def calc_te(temp, t_opt, t_base):

    r"""
    Calculates the temperature effect on the biomass rate
    ----
    Parameters
    ----------
    temp: ambient temperature as pd.series or list
    t_opt: optimum temperature for biomass growth
    t_base: base temperature for biomass growth
    Returns
    -------
    te : list of numerical values:
         temperature coefficients for calculating biomass rate

    """
    # Check if input arguments have proper type and length
    if not isinstance(temp, (list, pd.Series)):
        raise TypeError("Argument 'temp' is not of type list or pd.Series!")
    te = []    # creating a list
    # Calculate te
    for t in temp:
        if t < t_base:
            x = 0
            te.append(x)

        elif t_base <= t <= t_opt:
            x = (t-t_base)/(t_opt-t_base)
            te.append(x)

        elif t > t_opt:
            x = 1
            te.append(x)

    return te
