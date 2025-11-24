# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 20:36:19 2025

@author: David Mawson
"""
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from get_folderpaths import _ball_folder, MASTER_FOLDER
from get_fit_params import _errorbar, true_power_law, power_law, _log_linear_data, get_fit_params
from constants import BALL_DIAMETERS
from value_to_string import value_to_string
from fit_power_law_odr import fit_power_law_odr
import matplotlib.colors as mcolors
from itertools import cycle
import scicomap

balls = [
    {'name': 'ball1',
     'method': 'no-hold',
     'fluid': 'oil',},

    {'name': 'ball2',
     'method': 'no-hold',
     'fluid': 'oil',},

    {'name': 'ball3',
     'method': 'no-hold',
     'fluid': 'oil',},
    
    {'name': 'ball3_repeat',
     'method': 'no-hold',
     'fluid': 'oil',},
    
    {'name': 'ball4',
     'method': 'no-hold',
     'fluid': 'oil',}
]

crop_speed = (0, 0.0003)

log_scale = True
dimensionless = True
linear = True

SAVE_FIG = False
NEW_FIT = True
save_file = 'oil_no_hold.jpg'


#==============================================================================
# pick a colormap
cmap = plt.get_cmap('cmc.hawaii', 2*len(balls))


# generate reversed list of colours from the colormap
colors = [mcolors.to_hex(cmap(i)) for i in range(cmap.N)][::-1]

# set as the default color cycle
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

# Define linestyles and markers
linestyles = cycle(['-', '--', '-.', ':'])
markers = cycle(['o', 's', 'x', '^', 'v', '*', 'D', 'P'])

#==============================================================================

def load_data(ball_info):
    """Load data for a single ball."""
    ball_folder = _ball_folder(ball=ball_info['name'], fluid=ball_info['fluid'],
                               method=ball_info['method'])

    if dimensionless:
        return np.genfromtxt(ball_folder / "dimensionless_data.txt")
    else:
        return np.genfromtxt(ball_folder / "speed_pressure.txt")

def crop_data(data, ball_info):
    if 'cropping' in ball_info.keys():
        crop = ball_info['cropping']
    else:
        crop = crop_speed
    data = data[(crop[0]<data[:, 1]) & (data[:, 1]<crop[1]), :]
    return data

def reduced_chi_squared(y_fit, y, yerr):

    chi2 = np.sum(((y_fit - y) / yerr)**2)
    dof = len(y) - 2    # two fitted parameters
    return chi2 / dof

def effective_err(y_err, x_err, grad):
    return np.sqrt(y_err**2 + (grad * x_err)**2)
    
def comparison_plot():
    
    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(2, 1, height_ratios=[3, 1.2], hspace=0.25)
    ax = fig.add_subplot(gs[0, 0])
    ax_table = fig.add_subplot(gs[1, 0])
    ax_table.axis("off")
    # Construct table rows
    table_rows = []
    
    if dimensionless:
        if linear:
            xlabel = r"$\lambda$"
            ylabel = r"P(Z) - $P_{th}$"
        else:
            xlabel = r"$\lambda$"
            ylabel = r"P(Z)"
    else:
        xlabel = "Velocity, m/s"
        ylabel = "Pressure, Pa"

    results = []

    for ball in balls:
        data = load_data(ball)
        data = crop_data(data, ball)
        if len(data) < 10: 
            continue
        ball_folder = _ball_folder(ball=ball['name'], fluid=ball['fluid'],
                                   method=ball['method'])
        
        if NEW_FIT:
            beta, sd_beta = fit_power_law_odr(data)
        else:
            if not (ball_folder / 'fit_params.txt').exists():
                get_fit_params(ball_folder)
            if dimensionless:
                params = np.genfromtxt(ball_folder / 'fit_params.txt')[1]
            else:
                params = np.genfromtxt(ball_folder / 'fit_params.txt')[0]
            beta, sd_beta = params[:3], params[3:]
        
        if linear:
            data = _log_linear_data(data, beta)

        label = f"{ball['name']} {ball['method']} {ball['fluid']}"
        ball_size = BALL_DIAMETERS[ball['name'].split('_')[0]][0]

        ls = next(linestyles)
        mk = next(markers)
        _errorbar(data, label = fr"Diameter = {ball_size * 1000} mm", ax=ax, marker=mk)

        x_fit = np.linspace(np.min(data[:, 1]), np.max(data[:, 1]), len(data[:,0]))
        
        if linear:
            y_fit = true_power_law(beta, x_fit)
        else:
            y_fit = power_law(beta, x_fit)
            
        
        y_err_eff = effective_err(data[:, 3], data[:, 2], beta[0])
        chi_2 = reduced_chi_squared(y_fit, data[:, 0], y_err_eff)
        print(f"reduced chi squared = {chi_2:.2f}")
        
        ax.plot(x_fit, y_fit, linestyle=ls)

        table_rows.append([fr"{ball_size * 1000} mm",
                           fr"{value_to_string(beta[0],sd_beta[0])}",
                           fr"{value_to_string(beta[1], sd_beta[1])}"])
        
        results.append((label, beta, sd_beta))

    ax.scatter(0.0001, 0.001, label=r"$P(Z) = P_{th} + \beta \lambda^{\alpha}$", 
               linestyle ="",color = "white")
    ax.legend(fontsize = 12, loc = "best", ncols=2)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xlabel(xlabel, fontsize = 14)
    if log_scale:
        ax.set_xscale('log')
        ax.set_yscale('log')
        
    
    table = ax_table.table(
        cellText=table_rows,
        colLabels=["Ball Diameter", r"$\alpha$", r"$\beta$"],
        loc="center",
        cellLoc="center",
        )
    table.auto_set_font_size(False)
    table.set_fontsize(14)      # choose your size
    table.scale(1, 1.5) 
    
    if SAVE_FIG:
        plt.savefig(MASTER_FOLDER/('PLOTS')/(save_file), dpi=300)
    plt.show()


if __name__ == '__main__':
    comparison_plot()