#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 21:20:26 2025

@author: brunokeyworth
"""

from map_ball_path import map_ball_path
import matplotlib.pyplot as plt
from scipy import odr
import numpy as np

def linear_func(beta, x):
    m, c = beta
    return m * x + c

def get_speed_data(folder, disp):
    
    file_path = folder / 'position_time.txt'
    
    if not file_path.exists():
        map_ball_path(folder, disp)
        
    data = np.genfromtxt(file_path)
    
    return data[:, 0], data[:, 1], data[:, 2], data[:, 3]

def find_ball_speed(folder, disp=False, savefig=False):
    
    time, position, t_err, p_err = get_speed_data(folder, disp)
    
    model = odr.Model(linear_func)

    # Create a RealData object (includes errors)
    data = odr.RealData(time, position, sx=t_err, sy=p_err)
    
    # Create the ODR object
    odr_instance = odr.ODR(data, model, beta0=[100, 0])  # initial guess
    
    # Run the regression
    output = odr_instance.run()

    if disp:
        # Print results
        output.pprint()
        
        x_fit = np.linspace(0, np.max(time), 2)
        y_fit = output.beta[0] * x_fit + output.beta[1]
        
        fig, ax1 = plt.subplots()
        ax1.errorbar(time, position, xerr=t_err, yerr=p_err, fmt='o',
        linestyle='', color='black', markerfacecolor='red', markeredgecolor='black',
        markersize=4, ecolor='black', elinewidth=0.8, markeredgewidth=0.5)
        ax1.plot(x_fit, y_fit, color = "blue", linewidth = 2, label = f"gradient = ({output.beta[0]:.2f} ± {output.sd_beta[0]:.2f})\n intercept = {output.beta[1]:.2f} ± {output.sd_beta[1]:.2f}")
        ax1.set_ylabel("distance (cm)")
        ax1.set_xlabel("time (s)")
        ax1.set_title(folder.name)
        ax1.legend()
        ax1.grid()
        ax1.minorticks_on()
        if savefig:
            plt.savefig(folder / 'position_time.png' , dpi=300)
        plt.show()
        
    return np.absolute(output.beta[0]), output.sd_beta[0]
        