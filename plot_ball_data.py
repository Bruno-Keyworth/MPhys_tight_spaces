#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 22:35:26 2025

@author: brunokeyworth
"""
import matplotlib.pyplot as plt
import numpy as np
from get_folderpaths import MASTER_FOLDER

PRESSURE_ERROR = np.sqrt(0.2**2 +0.3**2)

def get_log_fit(data):

    log_pressure = np.log(data[:, 0])
    log_speed = np.log(data[:, 1])
    log_speed_err = data[:, 2] / data[:, 1]
    log_pressure_err = PRESSURE_ERROR / data[:, 0]

    

def plot_ball_data(ball, data):

    fig, ax = plt.subplots()
    ax.errorbar(data[:, 1], data[:, 0], xerr=data[:, 2], yerr=PRESSURE_ERROR, ls='', marker='.')
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel('Pressure (mbar)')
    ax.set_xlabel('Speed (cm/s)')

    plt.savefig(MASTER_FOLDER / ball / 'speed_pressure.png', dpi=300)
    plt.show()