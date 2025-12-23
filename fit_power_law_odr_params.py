import numpy as np
from scipy import odr

def fit_power_law_odr(data, beta0=None, verbose=True):
    """
    Fit y = b * x^a to data using ODR.
    data: Nx4 array -> columns [x, sx, y, sy]
    beta0: optional initial guess [a, b]
    Returns: fitted parameters (a, b) and their uncertainties
    """
    # unpack
    x = np.asarray(data[:, 0], dtype=float)
    sx = np.asarray(data[:, 1], dtype=float)
    y = np.asarray(data[:, 2], dtype=float)
    sy = np.asarray(data[:, 3], dtype=float)

    if x.size == 0 or y.size == 0:
        raise ValueError("Empty data provided.")

    # default initial guess
    if beta0 is None:
        a0 = -5   # negative exponent
        b0 = max(y) # positive coefficient
        beta0 = [a0, b0]

    # model function
    def power_law(B, x):
        a, b = B
        return b * x**a

    # create ODR instance
    model = odr.Model(power_law)
    odr_data = odr.RealData(x, y, sx=sx, sy=sy)
    odr_inst = odr.ODR(odr_data, model, beta0=beta0, iprint=1, maxit=1000)
    
    output = odr_inst.run()
    if verbose:
        output.pprint()

    # fitted parameters and uncertainties
    a_hat, b_hat = output.beta
    sd_a, sd_b = output.sd_beta

    # enforce sign constraints after fitting
    if b_hat < 0:
        print("Warning: fitted b < 0")
    if a_hat > 0:
        print("Warning: fitted a > 0")

    return (float(a_hat), float(b_hat)), (float(sd_a), float(sd_b))
