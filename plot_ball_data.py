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

def power_law(beta, x):
    return beta[2] + beta[1] * x**beta[0]

def get_log_fit(data):

    model = odr.Model(power_law)

    # Create a RealData object (includes errors)
    odr_data = odr.RealData(data[:, 1], data[:, 0], sx=data[:, 2], sy=np.linspace(PRESSURE_ERROR, PRESSURE_ERROR, len(data)))
    # Create the ODR object
    odr_instance = odr.ODR(odr_data, model, beta0=[0.5, 10, 30])  # initial guess

    # Run the regression
    output = odr_instance.run()
    output.pprint()

    return output.beta, output.sd_beta

def plot_ball_data(ball, data, version=None):

    beta, sd_beta = get_log_fit(data)
    
    x = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 100)
    y = power_law(beta, x)

    fig, ax = plt.subplots()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=PRESSURE_ERROR, ls='', marker='.')
    #ax.plot(x, y, label = r"$y=a+bx^\alpha$"+'\n'+fr" $\alpha$ = {beta[0]:.2f} ± {sd_beta[0]:.2f}"+'\n'+fr"  b = {beta[1]:.2f} ± {sd_beta[1]:.2f}"+'\n'+fr"  a = {beta[2]:.2f} ± {sd_beta[2]:.2f}")
    ax.set_ylabel('Pressure (mbar)')
    ax.set_xlabel('Speed (cm/s)')
    if version is None:
        save_name = 'speed_pressure.png'
    else:
        save_name = f'speed_pressure_{version}.png'

    ax.legend() 
    plt.savefig(MASTER_FOLDER / ball / save_name, dpi=300)
    ax.set_yscale('log')
    ax.set_xscale('log')
    plt.savefig(MASTER_FOLDER / ball / ('log_' + save_name), dpi=300)
    plt.show()