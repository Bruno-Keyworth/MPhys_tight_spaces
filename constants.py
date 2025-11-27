#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 21:33:20 2025

@author: brunokeyworth
"""
# measured length scale of the camera frame
FRAME_SIZE = 0.149 #m
FRAME_SIZE_ERR = 0.003/FRAME_SIZE # fractional error on frame size

# Errors
TIME_ERROR = 0.01 #s (timestamp)
FLUID_DEPTH_ERROR = 0.01 #m


FLUID_PARAMS = {
    'oil': {
        'density': [907, 45],# kg/m^3 from Thomas Sigsworth's report
        'viscosity': [0.069, 0.007] #Pas # measured by us
    },
    'glycerol': { #measured by us
        'density': [1252, 8], 
        'viscosity': [0.484, 0.005]
    }
}

# From Thomas Sigsworth's MPhys report
TUBE_PARAMS = { # value, error
    'radius': [0.00488, 0.00014], #
    'thickness': [0.00048, 0.00007],
    'young_modulus': [1.99e6, 1.36e5] #Pa
    }

ball_size_err = 0.0001
BALL_DIAMETERS = {
    'ball0': [0.009, ball_size_err],
    'ball1': [0.011, ball_size_err],
    'ball2': [0.012, ball_size_err],
    'ball3': [0.014, ball_size_err],
    'ball4': [0.016, ball_size_err],
    'ball5': [0.018, ball_size_err],
}

g = 9.81 #m/s^2