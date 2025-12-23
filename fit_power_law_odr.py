#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 22:07:05 2025

@author: brunokeyworth
"""
import numpy as np
from scipy import odr

def _safe_power_law(beta, x):
    """
    Model used by ODR: returns c + b * x**a for x expected to be pre-scaled.
    beta = [a, b, c]
    We guard against extreme beta[0] (a) values which produce overflow.
    """
    a, b, c = beta
    # clip x to safe positive domain (should already be scaled)
    x_safe = np.clip(x, 1e-300, 1e300)

    # discourage optimizer from exploring ridiculous exponents
    if np.isnan(a) or np.abs(a) > 100:
        # return large but finite numbers to give a large residual; avoids inf propagating
        return np.full_like(x_safe, 1e300)

    # compute power safely under numpy errstate
    with np.errstate(over='ignore', invalid='ignore'):
        # np.power may produce inf for some combos; we allow that because ODR handles large residuals
        y_model = c + b * np.power(x_safe, a)

    # if any values are inf or nan, convert to a very large finite number (so residual is huge)
    bad = ~np.isfinite(y_model)
    if np.any(bad):
        y_model[bad] = 1e300
    return y_model

def fit_power_law_odr(data, xscale=None, beta0=None, verbose=True, yscale=None):
    """
    Fit y = c + b * x^a to data with errors in x and y using scipy.odr.
    data: Nx4 array -> columns [y, x, sx, sy]
    xscale: optional scalar to scale x (if None it's set to max(|x|) or 1.0)
    beta0: optional initial guess [a, b, c] in the SCALED x-space
    Returns dict with fitted parameters in original x-units and uncertainties.
    """
    # unpack
    y = np.asarray(data[:, 0], dtype=float)
    x = np.asarray(data[:, 1], dtype=float)
    sx = np.asarray(data[:, 2], dtype=float)
    sy = np.asarray(data[:, 3], dtype=float)

    # check basic validity
    if x.size == 0 or y.size == 0:
        raise ValueError("Empty data provided.")

    # choose xscale
    if xscale is None:
        max_abs_x = np.max(np.abs(x))
        xscale = max_abs_x if max_abs_x != 0 else 1.0
        
    if yscale is None:
        yscale = np.max(np.abs(y)) or 1.0
        y_scaled = y / yscale
        sy_scaled = sy / yscale

    # scale x and sx so x_scaled is O(1)
    x_scaled = x / xscale
    sx_scaled = sx / xscale

    # sensible default initial guess in scaled space if not given
    if beta0 is None:
        a0 = 0.5
        median_xa = np.median(np.maximum(x_scaled, 1e-12) ** a0)
        b0 = (np.median(y_scaled) - np.min(y_scaled)) / (median_xa + 1e-12)
        c0 = np.min(y_scaled)
        beta0 = [a0, b0, c0]

    model = odr.Model(_safe_power_law)
    odr_data = odr.RealData(x_scaled, y_scaled, sx=sx_scaled, sy=sy_scaled)
    odr_inst = odr.ODR(odr_data, model, beta0=beta0, iprint=0)
    output = odr_inst.run()
    if verbose:
        output.pprint()

    a_hat, b_hat_scaled, c_hat_scaled = output.beta
    sd_a, sd_b_scaled, sd_c_scaled = output.sd_beta

    # Convert back to original units
    b_hat = b_hat_scaled * (yscale / (xscale ** a_hat))
    c_hat = c_hat_scaled * yscale
    sd_b = sd_b_scaled * (yscale / (xscale ** a_hat))
    sd_c = sd_c_scaled * yscale
    
    reduced_chi_squared = output.sum_square/(len(y)-3)

    return (float(a_hat), float(b_hat), float(c_hat)), (float(sd_a), float(sd_b), float(sd_c)), reduced_chi_squared
