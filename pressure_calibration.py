#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:09:36 2025

@author: brunokeyworth
"""

import numpy as np
import matplotlib.pyplot as plt

def get_error(voltage):
    
    return voltage * np.sqrt(0.01**2/voltage**2 + 0.001**2)

plt.close('all')

voltage_data = np.genfromtxt("../data/calibration_voltages.txt", delimiter=',', comments='%')

pressures = np.linspace(0, 2000, 21)

figure = plt.figure(figsize=(12, 8))

axes = figure.add_subplot(111)

delta_V = voltage_data[:, 0]-voltage_data[:, 1]

errors = np.sqrt(get_error(voltage_data[:, 0])**2 + get_error(voltage_data[:, 1])**2)

parameters, cov = np.polyfit(pressures, delta_V, w=1/errors, cov=True, deg=1)

x = np.linspace(0, 2000, 100)
y= np.polyval(parameters, x)

axes.errorbar(pressures, delta_V, yerr=errors, ls='', label='Data', marker='.')
axes.plot(x, y, c='r', ls='dashed', label='Best fit')
plt.legend()

axes.set_xlabel("Applied Pressure (mbar)")
axes.set_ylabel("Voltage Difference (mV)")

plt.savefig("../plots/voltage_difference.png")

figure = plt.figure(figsize=(12, 8))

axes = figure.add_subplot(111)

m = ['+', 'x']
l = ["2.9cm Oil", "7.7cm Oil"]
s = ['dashed', 'dotted']

for i, voltages in enumerate([voltage_data[:, 0], voltage_data[:, 1]]):

    errors = get_error(voltages)
    
    axes.errorbar(pressures, voltages, yerr=errors, ls='', marker=m[i], label='Data: '+l[i])
    
    parameters, cov = np.polyfit(pressures, voltages, w=1/errors, cov=True, deg=1)
    
    x = np.linspace(0, 2000, 100)
    y= np.polyval(parameters, x)
    
    axes.plot(x, y, ls=s[i], label='best fit: '+l[i])
    axes.set_xlabel("Applied Pressure (mbar)")
    axes.set_ylabel("Voltage (mV)")
    
    print(f"gradient = {parameters[0]:.5f} +/- {np.sqrt(cov[0][0]):.3f}")
    print(f"intercept = {parameters[1]:.5f} +/- {np.sqrt(cov[1][1]):.3f}")
    
plt.legend()
    
plt.savefig("../plots/voltage_pressure.png")