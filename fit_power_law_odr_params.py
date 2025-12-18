#!/usr/bin/env python3
import numpy as np
from scipy import odr

def _safe_power_law(beta, x):
    """
    Model: y = c + b * x^a
    Enforces physically expected signs:
      a < 0, b > 0, c > 0
    Returns huge residuals if parameters are out of bounds.
    """
    a, b, c = beta
    x_safe = np.clip(x, 1e-300, 1e300)
    
    # enforce expected signs
    if not (-10 < a < 0) or b < 0 or c < 0:
        return np.full_like(x_safe, 1e300)
    
    with np.errstate(over='ignore', invalid='ignore'):
        y_model = c + b * np.power(x_safe, a)
    
    # replace inf/nan with huge numbers
    y_model[~np.isfinite(y_model)] = 1e300
    return y_model

def fit_power_law_odr(data, xscale=None, beta0=None, verbose=True):
    """
    Fit y = c + b * x^a to data using ODR.
    data: Nx4 array -> columns [y, x, sx, sy]
    xscale: optional scalar to scale x (default = max(abs(x)))
    beta0: optional initial guess [a, b, c]
    Returns: fitted parameters (a, b, c) and their uncertainties
    """
    # unpack
    x = np.asarray(data[:, 0], dtype=float)
    sx = np.asarray(data[:, 1], dtype=float)
    y = np.asarray(data[:, 2], dtype=float)
    sy = np.asarray(data[:, 3], dtype=float)

    if x.size == 0 or y.size == 0:
        raise ValueError("Empty data provided.")

    # scale x to O(1)
    if xscale is None:
        xscale = np.max(np.abs(x)) or 1.0
    x_scaled = x / xscale
    sx_scaled = sx / xscale

    # y left in original units
    y_scaled = y
    sy_scaled = sy

    # default initial guess
    if beta0 is None:
        c0 = max(y_scaled) * 0.01
        b0 = max(y_scaled)
        a0 = -0.2
        beta0 = [a0, b0, c0]

    # create ODR instance
    model = odr.Model(_safe_power_law)
    odr_data = odr.RealData(x_scaled, y_scaled, sx=sx_scaled, sy=sy_scaled)
    odr_inst = odr.ODR(odr_data, model, beta0=beta0, iprint=1, maxit=1000)
    
    output = odr_inst.run()
    if verbose:
        output.pprint()

    # fitted parameters and uncertainties
    a_hat, b_hat, c_hat = output.beta
    sd_a, sd_b, sd_c = output.sd_beta

    return (float(a_hat), float(b_hat), float(c_hat)), (float(sd_a), float(sd_b), float(sd_c))
