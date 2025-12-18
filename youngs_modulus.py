#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 14:25:34 2025

This code is to reanalyse the data taken by Sajid Ahmed and Thomas Sigsworth in
their MPhys project in order to sort out a discrepency between the values given
by their two reports. 

@author: brunokeyworth
"""

from get_folderpaths import MASTER_FOLDER
import numpy as np
import matplotlib.pyplot as plt

folder = MASTER_FOLDER / 'youngs_modulus'

files = [folder / f for f in ['dry_1.txt', 'dry_2.txt', 'dry_3.txt', 'wet_1.txt', 
                              'wet_2.txt', 'wet_3.txt']]

sigsworth_values = np.array([1.401, 1.308, 1.319, 1.154, 1.165, 1.216]) * 1e6 # to get in Pa
ahmed_values = np.array([2.07, 2.07, 2.07, 1.91, 1.91, 1.91]) * 1e6

def get_E(file, value_1, value_2):
    data = np.genfromtxt(file, comments='%', usecols=(2, 3))
    plt.scatter(data[:, 0], data[:, 1])
    data = data[int(len(data)*0.4):, :]
    parameters, cov = np.polyfit(data[:, 0], data[:, 1], 1, cov=True)
    x = np.linspace(data[0, 0], data[-1, 0], 2)
    y = np.polyval(parameters, x)
    plt.plot(x, y, c='r', label = fr'$F/{{\Delta L}} = ${parameters[0]*1000:.1f} N/m' + '\n' 
             + fr'Sigsworth Requires $L/A = ${value_1/(parameters[0]*1000):.3f} m$^{{-1}}$' + '\n'
             + fr'Ahmed Requires $L/A = ${value_2/(parameters[0]*1000):.3f} m$^{{-1}}$')
    plt.xlabel('Extension (mm)')
    plt.ylabel('Force (N)')
    plt.title(f"{file.name.split('.')[0]}, Sigsworth: {value_1 *1e-6} MPa, Ahmed: {value_2 *1e-6} MPa")
    plt.legend()
    plt.savefig(folder / f"{file.name.split('.')[0]}.png", dpi=300)
    plt.show()
    print(parameters)
    print(value_1/(parameters[0]*1000))

for i, file in enumerate(files):
    get_E(file, sigsworth_values[i], ahmed_values[i])