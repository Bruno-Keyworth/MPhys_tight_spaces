#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 19:34:05 2025

@author: brunokeyworth
"""

import numpy as np

def order_of_magnitude(value):
    """
    Calculate the order of magnitude of a given numerical value.

    Parameters:
    - value (float): The numerical value for which the order of magnitude is to be calculated.

    Returns:
    - int: The order of magnitude of the input value. If the input is 0, returns -inf.
    """

    if value == 0:

        return -1 * np.inf

    return int(np.floor(np.log10(np.absolute(value))))

def value_to_string(value, error, sig_figs = 3, std_form=True):
    """
    Converts a value and its error to a formatted string with the specified
    number of significant figures. The result includes the measured value,
    the error, and the appropriate magnitude (if necessary).

    Parameters:
    - value (float): The value
    - error (float): The uncertainty associated with the value.
    - sig_figs (int): The desired number of significant figures.
    Default is 3.

    Returns:
    str: A formatted string representing the value and its error.
    """

    if not isinstance(sig_figs, int):

        print('Please set the number of significant figures to be an integer.')

        sig_figs = 3

    magnitude = order_of_magnitude(value)

    precision = sig_figs - 1

    if np.absolute(magnitude) < 2 or not std_form:

        return f'{value:.{precision}f} ± {error:.{precision}f}'

    value /= 10**magnitude

    error /= 10**magnitude

    return f'({value:.{precision}f} ± {error:.{precision}f})e{magnitude}'