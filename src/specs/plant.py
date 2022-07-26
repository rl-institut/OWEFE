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
    temp: ambient temperature pd.series
    Returns
    -------
    te : list of numerical values
        List of temperature coefficient for calculating biomass rate
    t_opt: optimum temperature for biomass growth
    t_base: base temperature for biomass growth
    """
    # Check if input arguments have proper type and length
    if not isinstance(temp, (list, pd.Series)):
        raise TypeError("Argument 'temp' is not of type list or pd.Series!")

    # Calculate te.

    te = temp-t_base/(t_opt-t_base)

    return te
