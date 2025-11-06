#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 22:00:59 2025

@author: brunokeyworth
"""
import numpy as np
from scipy import odr

def _safe_piecewise_power_law(beta, x):
    """
    Two-segment power law model for ODR:
    beta = [a1, b1, a2, b2, c, x0]
    Optionally continuous at x0 if you want to enforce it (see below).
    """
    a1, b1, a2, b2, c, x0 = beta
    x_safe = np.clip(x, 1e-300, 1e300)

    # handle nonsense values
    if np.any(np.isnan(beta)) or np.any(np.abs(beta[:4]) > 100):
        return np.full_like(x_safe, 1e300)

    # compute two regimes
    with np.errstate(over='ignore', invalid='ignore'):
        y = np.empty_like(x_safe)
        mask = x_safe <= x0
        y[mask] = c + b1 * (x_safe[mask] / x0) ** a1
        y[~mask] = c + b2 * (x_safe[~mask] / x0) ** a2

    bad = ~np.isfinite(y)
    y[bad] = 1e300
    return y


def fit_piecewise_power_law_odr(data, xscale=None, beta0=None, continuous=True, verbose=True):
    """
    Fit a two-segment power law to data using scipy.odr.
    data: Nx4 array -> [y, x, sx, sy]
    If continuous=True, b2 is adjusted internally so the two branches meet at x0.
    """
    y = np.asarray(data[:, 0], float)
    x = np.asarray(data[:, 1], float)
    sx = np.asarray(data[:, 2], float)
    sy = np.asarray(data[:, 3], float)

    if x.size == 0 or y.size == 0:
        raise ValueError("Empty data provided.")

    if xscale is None:
        max_abs_x = np.max(np.abs(x))
        xscale = max_abs_x if max_abs_x != 0 else 1.0

    x_scaled = x / xscale
    sx_scaled = sx / xscale

    # Initial guess
    if beta0 is None:
        x0_guess = np.median(x_scaled)
        a1, a2 = 0.5, 0.5
        b1, b2 = (np.max(y) - np.min(y)) / (x0_guess ** a1 + 1e-12), (np.max(y) - np.min(y)) / (x0_guess ** a2 + 1e-12)
        c = np.min(y)
        beta0 = [a1, b1, a2, b2, c, x0_guess]

    # If continuity enforced: reduce parameter count by expressing b2 in terms of others
    if continuous:
        def _continuous_model(beta_reduced, x):
            a1, b1, a2, c, x0 = beta_reduced
            x_safe = np.clip(x, 1e-300, 1e300)
            with np.errstate(over='ignore', invalid='ignore'):
                y = np.empty_like(x_safe)
                mask = x_safe <= x0
                y[mask] = c + b1 * (x_safe[mask] / x0) ** a1
                # enforce continuity at x0: c + b2 = c + b1 ⇒ b2 = b1 * x0^(a1 - a2)
                b2 = b1 * x0 ** (a1 - a2)
                y[~mask] = c + b2 * (x_safe[~mask] / x0) ** a2
            bad = ~np.isfinite(y)
            y[bad] = 1e300
            return y

        model = odr.Model(_continuous_model)
        odr_data = odr.RealData(x_scaled, y, sx=sx_scaled, sy=sy)
        beta0_reduced = beta0[:2] + [beta0[2]] + [beta0[4], beta0[5]]  # [a1, b1, a2, c, x0]
        odr_instance = odr.ODR(odr_data, model, beta0=beta0_reduced)
    else:
        model = odr.Model(_safe_piecewise_power_law)
        odr_data = odr.RealData(x_scaled, y, sx=sx_scaled, sy=sy)
        odr_instance = odr.ODR(odr_data, model, beta0=beta0)

    output = odr_instance.run()
    if verbose:
        output.pprint()

    return output
