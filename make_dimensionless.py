#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 14:22:33 2025

@author: brunokeyworth
"""
import numpy as np
# From last year report
YOUNG_MODULUS = 1.99e6 #Pa
YOUNG_MODULUS_ERR = 1.36e5

VISCOSITY = { #Pas
    'oil': [0.0729, 0.0028], #value, error
    'glycerol': [1.49, 0.01] #from google
}

# Estimate, we need to measure
TUBE_RADIUS = 0.00488
TUBE_RADIUS_ERR = 0.00014
TUBE_THICK = 0.00048
TUBE_THICK_ERR = 0.00007

ball_size_err = 0.0001
ball_sizes = { #metres
    'ball0': 0.009,
    'ball1': 0.011,
    'ball2': 0.012,
    'ball3': 0.014,
    'ball4': 0.016,
    'ball5': 0.018,
    }

def _get_L(R, R_err=ball_size_err, a=TUBE_RADIUS, a_err=TUBE_RADIUS_ERR):
    L = 2 * np.sqrt(R**2 - a**2)
    L_err = np.sqrt(
        ((2 * R / np.sqrt(R**2 - a**2)) * R_err)**2 +
        ((-2 * a / np.sqrt(R**2 - a**2)) * a_err)**2
    )
    return L, L_err

def _get_delta3(R, R_err=ball_size_err, a=TUBE_RADIUS, a_err=TUBE_RADIUS_ERR):
    delta3 = (R - a)**3
    delta3_err = 3 * (R - a)**2 * np.sqrt(R_err**2 + a_err**2)
    return delta3, delta3_err

def _get_lambda(V, V_err, R, R_err=ball_size_err, a=TUBE_RADIUS, a_err=TUBE_RADIUS_ERR,
                E=YOUNG_MODULUS, E_err=YOUNG_MODULUS_ERR, mu=VISCOSITY, mu_err=VISCOSITY_ERR,
                b=TUBE_THICK, b_err=TUBE_THICK_ERR):
    
    delta3, delta3_err = _get_delta3(R, R_err, a, a_err)
    L, L_err = _get_L(R, R_err, a, a_err)
    
    lamb = 6 * mu * V * a**2 * L / (E * b * delta3)
    
    # relative uncertainty propagation
    rel_err_sq = (
        (mu_err / mu)**2 +
        (V_err / V)**2 +
        (2 * a_err / a)**2 +
        (L_err / L)**2 +
        (E_err / E)**2 +
        (b_err / b)**2 +
        (delta3_err / delta3)**2
    )
    
    lamb_err = abs(lamb) * np.sqrt(rel_err_sq)
    return lamb, lamb_err

def _get_dimensionless_pressure(P, P_err, R, R_err=ball_size_err, 
                                E=YOUNG_MODULUS, E_err=YOUNG_MODULUS_ERR,
                                b=TUBE_THICK, b_err=TUBE_THICK_ERR, 
                                a=TUBE_RADIUS, a_err=TUBE_RADIUS_ERR):
    delta = R - a
    delta_err = np.sqrt(R_err**2 + a_err**2)
    
    P_s = E * b * delta / a**2
    
    # dimensionless pressure
    P_dimless = P / P_s
    
    # relative uncertainty in P_s
    rel_Ps_err_sq = (
        (E_err / E)**2 +
        (b_err / b)**2 +
        (delta_err / delta)**2 +
        (2 * a_err / a)**2
    )
    
    rel_P_err_sq = (P_err / P)**2 + rel_Ps_err_sq
    
    P_dimless_err = abs(P_dimless) * np.sqrt(rel_P_err_sq)
    
    return P_dimless, P_dimless_err
    

def make_dimensionless(data, data_file):
    
    ball = data_file.parent.name
    fluid = data_file.parent.parent.parent.name
    
    ball_size = ball_sizes[ball.split('_')[0]]
    
    viscosity = VISCOSITY[fluid]
    
    lamb, error = _get_lambda(data[:, 1], data[:, 2], ball_size, mu=viscosity[0], mu_err=viscosity[1])
    P, P_err = _get_dimensionless_pressure(data[:, 0], data[:, 3], ball_size)
    
    return np.column_stack((P, lamb, error, P_err))