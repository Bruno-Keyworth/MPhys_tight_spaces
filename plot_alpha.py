#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 09:44:25 2025

@author: brunokeyworth
"""

from get_preset import *
import numpy as np
import matplotlib.pyplot as plt
from get_folderpaths import _ball_folder
from constants import BALL_DIAMETERS

def get_alpha(ball):
    params_file = _ball_folder(ball_dict=ball) / 'fit_params.txt'
    if not params_file.exists():
        return None, None
    alphas = np.genfromtxt(params_file, usecols=(0, 3))
    return alphas[1, :], alphas[0, :]

def get_alphas(balls):
    
    ball_sizes = []
    alphas = []    
    dimless_alphas = []
    for ball in balls:
        # dimless_alpha refers to alpha obtained through fitting to the dimensionless data;
        # both alpha are dimensionless values.
        alpha, dimless_alpha, = get_alpha(ball)
        if alpha is None:
            continue
        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]]
        ball_sizes.append(ball_size)
        alphas.append(alpha)
        dimless_alphas.append(dimless_alpha)
        
    return np.column_stack((ball_sizes, alphas, dimless_alphas))
        