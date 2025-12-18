#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 20:56:53 2025

@author: brunokeyworth
"""
from scipy.optimize import curve_fit
import numpy as np

def power_law_neg(x, a, b, c):
    return c - b * x**a

def fit_power_law_simple(data):
    y = data[:,0]
    x = data[:,1]

    # initial guess
    c0 = 1.01 * np.max(y)
    b0 = c0 - np.min(y)
    a0 = -1.0
    p0 = [a0, b0, c0]

    lower = [-10, 0, np.max(y)]
    upper = [0, np.inf, np.inf]

    popt, _ = curve_fit(power_law_neg, x, y, p0=p0, bounds=(lower, upper), maxfev=10000)
    return popt