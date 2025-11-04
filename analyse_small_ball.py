#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 10:08:24 2025

@author: brunokeyworth
"""
from get_folderpaths import MASTER_FOLDER
from analyse_ball import analyse_ball
from plot_ball_data import _errorbar
import numpy as np
import matplotlib.pyplot as plt

BALL = 'ball0'

def plot_small_ball(ball):
    filepath = MASTER_FOLDER / ball / 'speed_pressure.txt'
    
    data = np.genfromtxt(filepath)
    
    parameters = np.polyfit(data[2:-3, 1], data[2:-3, 0], 1)
    
    x = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), 2)
    y = np.polyval(parameters, x)
    
    fig, ax = plt.subplots()
    ax.plot(x, y, label=f'Gradient = {parameters[0]}' + '\n' + f'Intercept = {parameters[1]}')
    _errorbar(data, dimensions=True)
    plt.savefig(MASTER_FOLDER / ball / 'plot.png', dpi=300)
    

def analyse_small_ball(ball=BALL):
    
    analyse_ball(ball, plot=False)
    plot_small_ball(ball)
    
if __name__ == '__main__':
    analyse_small_ball()