#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 11:11:55 2025

@author: brunokeyworth
"""

from find_ball_speed import get_speed_data
import matplotlib.pyplot as plt
import numpy as np
from scipy import odr
from get_folderpaths import get_folderpaths, MASTER_FOLDER
from analyse_ball import sort_folder
    

def piecewise_cubic(beta, x):
    """
    Piecewise function:
        y = y0                                              for x < x0
        y = y0 + a*(x - x0)^3 + b*(x - x0)^2 + c*(x - x0)   for x0 <= x <= x1
        y = y0 + a*(x1 - x0)**3 + b*(x1 - x0)**2 + c*(x1 - x0) + m2*(x - x1)   for x > x1
    """
    x0, x1, y0, a, b, c, m2 = beta

    y = np.piecewise(
        x,
        [x < x0, (x >= x0) & (x <= x1), x > x1],
        [
            lambda x: y0,
            lambda x: y0 + a*(x - x0)**3 + b*(x - x0)**2 + c*(x - x0),
            lambda x: (
                y0
                + a*(x1 - x0)**3
                + b*(x1 - x0)**2
                + c*(x1 - x0)
                + m2*(x - x1)
            ),
        ]
    )
    return y


def fit_piecewise_cubic_odr(data):
    """
    Fit a piecewise cubic model: flat → cubic → linear
    data[:,0] = x (time)
    data[:,1] = y (position)
    data[:,2] = sx (optional, can be zeros)
    data[:,3] = sy (optional, can be zeros)
    """
    model = odr.Model(piecewise_cubic)
    real_data = odr.RealData(data[:, 0], data[:, 1], sx=data[:, 2], sy=data[:, 3])

    # Rough initial guesses
    x = data[:, 0]
    y = data[:, 1]
    x0_guess = x[0] + 0.1 * (x[-1] - x[0])
    x1_guess = x[0] + 0.5 * (x[-1] - x[0])
    y0_guess = y[0]
    m2_guess = (y[-1] - y[0]) / (x[-1] - x[0])

    a_guess = 0.0
    b_guess = 0.1
    c_guess = m2_guess / 2  # roughly half the final slope inside region

    odr_instance = odr.ODR(
        real_data,
        model,
        beta0=[x0_guess, x1_guess, y0_guess, a_guess, b_guess, c_guess, m2_guess],
    )
    output = odr_instance.run()
    return output.beta, output.sd_beta

def get_constant_v_region(data):
    x = data[:, 1]
    t = data[:, 0]
    v = np.gradient(x, t)  # numerical derivative
    a = np.gradient(v, t)
    
    # Find the time index where acceleration first becomes ~0
    # (you might want to smooth first)
    from scipy.ndimage import uniform_filter1d
    a_smooth = uniform_filter1d(a, size=5)
    
    # e.g., when acceleration magnitude drops below a threshold and stays low
    threshold = 0.01 * np.max(np.abs(a_smooth))
    flat = np.abs(a_smooth) < threshold
    
    # Find first time from which it's "mostly flat" onwards
    for i in range(len(flat)):
        if all(flat[i:]):
            t_constant = t[i]
            break
    else:
        t_constant = None  # not found
        
    return t_constant

def find_flat_region(data):
    
    initial_position = np.mean(data[:20, 0])
    error = np.max(np.absolute(data[:20, 0]-initial_position))
    start = data[-1, 0]
    for row in data[20:, :]:
        if row[0] > initial_position + 2 * error:
            start = row[0]
            break
    return start

def get_accelaration_time(folder):
   data = get_speed_data(folder, disp=True)
   
   #beta, sd_beta = fit_piecewise_cubic_odr(data)
   
   # x = np.linspace(data[0, 0], data[-1, 0], 100)
   # y = piecewise_cubic(beta, x)
   
   fig, ax = plt.subplots()
   # t0 = find_flat_region(data)
   # t1 = get_constant_v_region(data)
   
   ax.errorbar(data[:, 0], data[:, 1], xerr=data[:, 2], yerr=data[:, 3], c='b', alpha=0.5)
   ax.set_title(folder.parent.name + ' ' + folder.name)
   
   #ax.plot(x, y, c='r')
   # ax.axvline(t0, ls='dashed', c='k')
   # if t1 is not None:
   #     ax.axvline(t1, ls='dashed', c='k')
   plt.savefig(folder, dpi=300)
   
for i in range(5):
    sort_folder(MASTER_FOLDER / 'acceleration' / f'ball{i+1}_acceleration')
    folders = get_folderpaths(f'acceleration/ball{i+1}_acceleration')
    for folder, _, _ in folders:
   
        get_accelaration_time(folder)
    
    