#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 14:05:58 2025

@author: brunokeyworth
"""

from get_folderpaths import MASTER_FOLDER
from value_to_string import value_to_string
import numpy as np
import matplotlib.pyplot as plt

viscosity_folder = MASTER_FOLDER / 'viscosity'

file_names = {
    "oil": "oil3.txt",
    "glycerol": "glycerol4.txt",
    "fresh glycerol": "glycerol2.txt"
    }

def get_viscosities(fluid):
    
    data = np.genfromtxt(viscosity_folder / file_names[fluid])[4:, :]
    
    parameters, cov = np.polyfit(data[:, 1], data[:, 0], 1, cov=True)
    print(fluid + ': ', parameters[1] )
    
    y =np.linspace(min(data[:, 1]), max(data[:, 1]), 100)
    x = np.polyval(parameters, y)
    
    viscosity, _ = parameters
    err = np.sqrt(cov[0][0])
    
    viscosity2 = np.mean(data[:,2])
    err2 = np.std(data[:, 2])
    
    plt.scatter(data[:, 0], data[:, 1], s=5)
    plt.plot(x, y, label=f'{fluid}: fitted viscosity = {value_to_string(parameters[0], err)} Pas' +
             '\n' + f'average viscosity = {value_to_string(viscosity2, err2)} Pas')
    
    return [viscosity, err], [viscosity2, err2]

for fluid in file_names.keys():
    
    get_viscosities(fluid)

#plt.xscale('log')
plt.legend()