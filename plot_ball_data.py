#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 22:35:26 2025

@author: brunokeyworth
"""
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER
from scipy import odr

PRESSURE_ERROR = np.sqrt(0.2**2 +0.3**2)

def exponential_function(beta, x):
    return np.exp(beta[1]) * x**beta[0]

def get_log_fit(data):

    model = odr.Model(exponential_function)

    # Create a RealData object (includes errors)
    odr_data = odr.RealData(data[:, 1], data[:, 0], sx=data[:, 2], sy=np.linspace(PRESSURE_ERROR, PRESSURE_ERROR, len(data)))
    # Create the ODR object
    odr_instance = odr.ODR(odr_data, model, beta0=[0.5, 10])  # initial guess

    # Run the regression
    output = odr_instance.run()
    output.pprint()

    return output.beta, output.sd_beta

def plot_ball_data(ball, data):

    beta, sd_beta = get_log_fit(data)
    
    x = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 100)
    y = exponential_function(beta, x)

    fig, ax = plt.subplots()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=PRESSURE_ERROR, ls='', marker='.')
    ax.plot(x, y)
    # ax.set_yscale('log')
    # ax.set_xscale('log')
    ax.set_ylabel('Pressure (mbar)')
    ax.set_xlabel('Speed (cm/s)')

    plt.savefig(MASTER_FOLDER / ball / 'speed_pressure.png', dpi=300)
    plt.show()