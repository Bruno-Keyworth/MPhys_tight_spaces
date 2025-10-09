#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:09:36 2025

@author: brunokeyworth
"""

import numpy as np
import matplotlib.pyplot as plt

plt.close('all')

voltages = np.genfromtxt("calibration_voltages.txt")

pressures = np.linspace(0, 2000, 21)

errors = voltages * np.sqrt(0.01**2/voltages**2 + 0.001**2)

figure = plt.figure(figsize=(12, 8))

axes = figure.add_subplot(111)

axes.errorbar(pressures, voltages, yerr=errors, ls='', marker='.')

parameters, cov = np.polyfit(pressures, voltages, w=1/errors, cov=True, deg=1)

x = np.linspace(0, 2000, 100)
y= np.polyval(parameters, x)

axes.plot(x, y)

print(f"gradient = {parameters[0]:.3f} +/- {np.sqrt(cov[0][0]):.3f}")
print(f"intercept = {parameters[1]:.3f} +/- {np.sqrt(cov[1][1]):.3f}")