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

def fit_power_law_odr(data, xscale=None, beta0=None, verbose=True):
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

    # scale x and sx so x_scaled is O(1)
    x_scaled = x / xscale
    sx_scaled = sx / xscale

    # sensible default initial guess in scaled space if not given
    if beta0 is None:
        a0 = 0.5
        # rough b0: (median(y)-min(y)) / median(x^a)
        median_xa = np.median(np.maximum(x_scaled, 1e-12) ** a0)
        b0 = (np.median(y) - np.min(y)) / (median_xa + 1e-12)
        c0 = np.min(y)
        beta0 = [a0, b0, c0]

    # create ODR objects
    model = odr.Model(_safe_power_law)
    odr_data = odr.RealData(x_scaled, y, sx=sx_scaled, sy=sy)
    odr_instance = odr.ODR(odr_data, model, beta0=beta0, iprint=0)

    # run
    output = odr_instance.run()
    if verbose:
        output.pprint()

    # raw fitted params in scaled-space
    a_hat, b_hat_scaled, c_hat = output.beta
    sd_a, sd_b_scaled, sd_c = output.sd_beta

    # convert b back to original x-units:
    # model used: y = c + b_hat_scaled * (x/xscale)^a_hat = c + (b_hat_scaled / xscale^a_hat) * x^a_hat
    b_hat = b_hat_scaled / (xscale ** a_hat)

    # propagate sd for b_hat via delta method using (a_hat, b_hat_scaled) uncertainties.
    # we attempt to use cov_beta if available to include covariance term.
    cov = None
    try:
        cov = output.cov_beta  # may be None or a matrix
    except Exception:
        cov = None

    # get covariance elements if present, otherwise assume zero covariance between a and b
    cov_ab = cov[0, 1] if (cov is not None and cov.shape == (3, 3)) else 0.0

    # avoid divide by zero when b_hat_scaled ~ 0
    if np.abs(b_hat_scaled) > 0:
        # derivative w.r.t b_hat_scaled: db/dbs = 1 / xscale^a
        # derivative w.r.t a: db/da = b_hat_scaled * (-ln(xscale)) / xscale^a = -b_hat * ln(xscale)
        # variance approximated: var(b) ≈ (db/dbs)^2 var(b_s) + (db/da)^2 var(a) + 2 (db/dbs)(db/da) cov(a,b_s)
        db_dbs = 1.0 / (xscale ** a_hat)
        db_da = -b_hat * np.log(xscale)
        var_b = (db_dbs ** 2) * (sd_b_scaled ** 2) + (db_da ** 2) * (sd_a ** 2) + 2 * db_dbs * db_da * cov_ab
        sd_b = np.sqrt(var_b) if var_b > 0 else np.abs(b_hat) * 1e-6
    else:
        # fallback: scale sd_b_scaled
        sd_b = sd_b_scaled / (xscale ** a_hat)

    return (float(a_hat), float(b_hat), float(c_hat)), (float(sd_a), float(sd_b), float(sd_c))
