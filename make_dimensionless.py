#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 14:22:33 2025

@author: brunokeyworth
"""
import numpy as np
from constants import BALL_DIAMETERS, TUBE_PARAMS, FLUID_PARAMS

def _get_L(ball_radius, tube_radius = TUBE_PARAMS['radius']):
    a, a_err = tube_radius
    R, R_err = ball_radius
    L = 2 * np.sqrt(R**2 - a**2)
    L_err = np.sqrt(
        ((2 * R / np.sqrt(R**2 - a**2)) * R_err)**2 +
        ((-2 * a / np.sqrt(R**2 - a**2)) * a_err)**2
    )
    return L, L_err

def _get_delta3(ball_radius, tube_radius = TUBE_PARAMS['radius']):
    a, a_err = tube_radius
    R, R_err = ball_radius
    
    delta3 = (R - a)**3
    delta3_err = 3 * (R - a)**2 * np.sqrt(R_err**2 + a_err**2)
    return delta3, delta3_err

def _get_delta(ball, tube_radius=TUBE_PARAMS['radius']):
    
    R, R_err = np.array(BALL_DIAMETERS[ball]) / 2
    a, a_err = np.array(tube_radius) / 2
    
    delta = R - a
    error = np.sqrt(R_err**2 + a_err**2)
    
    return delta, error

def _get_lambda(V, V_err, ball_diameter, viscosity, tube_params=TUBE_PARAMS):
    mu, mu_err = viscosity
    a, a_err = tube_params['radius']
    b, b_err = tube_params['thickness']
    E, E_err = tube_params['young_modulus']
    
    delta3, delta3_err = _get_delta3(ball_diameter, tube_params['radius'])
    L, L_err = _get_L(ball_diameter, tube_params['radius'])
    
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

def _get_dimless_pressure(P, P_err, ball_diameter, tube_params=TUBE_PARAMS):
    # turn ball_diameter into a 2-column array
    bd = np.asarray(ball_diameter, dtype=float)
    if bd.ndim == 1:
        # expected shape: (2,) → broadcast to match P
        if bd.size != 2:
            raise ValueError("ball_diameter must be [value, error] or an Nx2 array.")
        bd = np.tile(bd, (len(P), 1))
    elif bd.ndim == 2 and bd.shape[1] == 2:
        if bd.shape[0] != len(P):
            raise ValueError("ball_diameter array must have same number of rows as P.")
    else:
        raise ValueError("ball_diameter must be [value, error] or an Nx2 array.")
    
    # now bd[:,0] is value, bd[:,1] is error
    R     = bd[:,0] / 2
    R_err = bd[:,1] / 2
    a, a_err = tube_params['radius']
    b, b_err = tube_params['thickness']
    E, E_err = tube_params['young_modulus']
    
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
    
    ball_diameter = BALL_DIAMETERS[ball.split('_')[0]]
    
    viscosity = FLUID_PARAMS[fluid]['viscosity']
    
    lamb, error = _get_lambda(data[:, 1], data[:, 2], ball_diameter, viscosity=viscosity)
    P, P_err = _get_dimless_pressure(data[:, 0], data[:, 3], ball_diameter)
    
    return np.column_stack((P, lamb, error, P_err))