# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 11:28:20 2024

@author: david
"""
import numpy as np
import scipy.constants as sc
data = np.genfromtxt('pressure_test_data.txt',delimiter = ',')


x= data[:,0]
y = data[:,1] 
err = np.sqrt((y * 0.001)**2 + 0.01**2)


output_data = np.column_stack((x, y, err))
np.savetxt('corrected_pressure_test_data.txt', output_data, delimiter=',', header='x,y,err', comments='')