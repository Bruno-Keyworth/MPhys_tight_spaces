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
from value_to_string import value_to_string

def linear_func(beta, x):
    m, c = beta
    return m * x + c

def get_speed_data(folder, disp):
    
    file_path = folder / 'position_time.txt'
    
    if not file_path.exists():
        map_ball_path(folder, disp)
        
    data = np.genfromtxt(file_path)
    
    return data

def _get_effective_error(gradient, x_err, y_err):
    
    return y_err + np.absolute(x_err * gradient)

def plot_errors(time, position, t_err, p_err, gradient):
    
    ax = plt.gca()
    
    error = _get_effective_error(gradient, t_err, p_err)
    upper_bound = position + error
    lower_bound = position - error
    ax.fill_between(time, lower_bound, upper_bound, alpha=0.6, label='Within 1 error bar', color='lightblue')
    ax.plot(time, upper_bound, c='b', ls='dashed', alpha=0.7, linewidth=0.4)
    ax.plot(time, lower_bound, c='b', ls='dashed', alpha=0.7, linewidth=0.4)

def find_ball_speed(folder, disp=False, savefig=False):
    
    data = get_speed_data(folder, disp=False)
    
    time, position, t_err, p_err = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
    
    model = odr.Model(linear_func)

    # Create a RealData object (includes errors)
    data = odr.RealData(time, position, sx=t_err, sy=p_err)
    
    # Create the ODR object
    odr_instance = odr.ODR(data, model, beta0=[100, 0], iprint=0)  # initial guess
    
    # Run the regression
    output = odr_instance.run()

    if disp:
        # Print results
        output.pprint()
        
        x_fit = np.linspace(0, np.max(time), 2)
        y_fit = output.beta[0] * x_fit + output.beta[1]

        fig, ax1 = plt.subplots(figsize=(12, 6))
        plot_errors(time, position, t_err, p_err, output.beta[0])
        ax1.scatter(time, position, s=30, marker='x', c='b', label='Image Data')
        print(output.sd_beta)
        ax1.plot(x_fit, y_fit, color = "red", linewidth = 1, 
   label = rf"Fitted $V$ = {value_to_string(output.beta[0], output.sd_beta[0], sig_figs=4)} m$\,$s$^{{-1}}$")
        ax1.set_ylabel("Fitted Centre Position (m)", fontsize=20)
        ax1.set_xlabel("Time (s)", fontsize=20)
        #ax1.set_title(folder.name)
        ax1.legend(framealpha=0, fontsize=20)
        ax1.set_yticks([0, 0.05, 0.1, 0.15])
        plt.tick_params(labelsize=14)
        #ax1.grid()
        #ax1.minorticks_on()
        if savefig:
            plt.tight_layout()
            plt.savefig(folder / 'position_time.png' , dpi=300)
        #plt.show()
    plt.close('all')
    return np.absolute(output.beta[0]), output.sd_beta[0]
        