
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 18:27:02 2025

@author: David Mawson 

Threshold Pressure
"""
from constants import BALL_DIAMETERS
from get_folderpaths import MASTER_FOLDER, PLOTS_FOLDER, _ball_folder
from value_to_string import value_to_string
from get_fit_params import get_fit_params
import numpy as  np
import matplotlib.pyplot as plt
import pickle
import os
import re
from collections import defaultdict
from make_dimensionless import _get_dimless_pressure

pressure_err = 10  # mbar uncertainty

pressure_pattern = re.compile(r"(\d+)\s*mbar", re.IGNORECASE)
ball_base_pattern = re.compile(r"(ball\d+)")  # captures ball1 from ball1_repeat

threshold_path = MASTER_FOLDER / "threshold_data.pkl"

def _level4():
    return dict()
def _level3():
    return defaultdict(_level4)
def _level2():
    return defaultdict(_level3)
def level1():
    return defaultdict(_level2)

def save_results(results):
    save_dict = level1()
    for fluid, method_data in results.items():
        for method, ball_data in method_data.items():
    
            balls = []
            diameters = []
            pressures = []
            fitted_P = []
            dimless_fitted_P = []
    
            for ball, p in ball_data.items():
                if ball not in BALL_DIAMETERS:
                    continue
    
                diam = BALL_DIAMETERS[ball]
                balls.append(ball)
                diameters.append(diam)
                pressures.append(np.array(p)*100)
                
                param_file = _ball_folder(ball, fluid, method) / 'fit_params.txt'
                if not param_file.exists():
                    get_fit_params(_ball_folder(ball, fluid, method))
                
                params = np.genfromtxt(param_file, usecols=(2, 5))
                
                fitted_P.append(params[0, :])
                dimless_fitted_P.append(params[1, :])
    
            if not balls:
                continue
    
            diameters = np.array(diameters)
            pressures = np.array(pressures)
            dimless_P, err = _get_dimless_pressure(pressures[:, 0], pressures[:, 1], diameters)
            
            data = np.column_stack((diameters, pressures))
            dimless_data = np.column_stack((diameters, dimless_P, err))
            save_dict[fluid][method]['observed']['dimensional'] = data
            save_dict[fluid][method]['observed']['non-dimensional'] = dimless_data
            
            fitted_data = np.column_stack((diameters, fitted_P, err))
            dimless_fitted_data = np.column_stack((diameters, dimless_fitted_P, err))
            save_dict[fluid][method]['fitted']['dimensional'] = fitted_data
            save_dict[fluid][method]['fitted']['non-dimensional'] = dimless_fitted_data

    with open(threshold_path, "wb") as f:
        pickle.dump(save_dict, f)

def get_thresholds():

    results = defaultdict(lambda: defaultdict(dict))
    
    for fluid in os.listdir(MASTER_FOLDER):
        fluid_path = os.path.join(MASTER_FOLDER, fluid)
        if not (os.path.isdir(fluid_path) and fluid in ['oil', 'glycerol']):
            continue
    
        for method in os.listdir(fluid_path):
            method_path = os.path.join(fluid_path, method)
            if not os.path.isdir(method_path) :
                continue

            # e.g. ball3 and ball3_repeat both "ball3"
            ball_pressures = defaultdict(list)
    
            for ball in os.listdir(method_path):
                ball_path = os.path.join(method_path, ball)
                if not os.path.isdir(ball_path):
                    continue

                m = ball_base_pattern.match(ball)
                if not m:
                    continue
                base_ball_name = m.group(1)
    
                pressures = []
    
                for pressure_folder in os.listdir(ball_path):
                    pm = pressure_pattern.search(pressure_folder)
                    if not pm:
                        continue
    
                    pressures.append(int(pm.group(1)))
    
                if pressures:
                    lowest_pressure_for_this_ball = min(pressures)
                    ball_pressures[base_ball_name].append(lowest_pressure_for_this_ball)
    
            # Average repeated runs
            for base_ball_name, values in ball_pressures.items():
                avg_lowest_pressure = np.mean(values)
                std = np.std(values)
                if std < pressure_err:
                    err = pressure_err
                else:
                    err = std
                results[fluid][method][base_ball_name] = [avg_lowest_pressure, err]
    save_results(results)

def print_results(results):
    if PRINT:
        for fluid, method_data in results.items():
            print(f"\n=== {fluid.upper()} ===")
            for method, ball_data in method_data.items():
                print(f"  -- {method} --")
                for ball, p in ball_data.items():
                    print(f" {ball}: lowest averaged pressure = {value_to_string(p[0], p[1])} mbar")

def _add_to_plot(data, ax, label, fmt, colour, scale=1):
    # Plot with distinct colour + marker
    ax.errorbar(
        data[:, 0]*1000,
        data[:, 2]/scale,
        xerr=data[:, 1]*1000,
        yerr=data[:, 3]/scale,
        fmt=fmt,
        color=colour,
        ecolor='black',
        elinewidth=1,
        capsize=3,
        label=label,
    )

def plot_threshold(results):
    colours = {
    'oil': 'tab:red',
    'glycerol': 'tab:blue'
    }
    
    fitted_cmap = {
        'oil': 'r',
        'glycerol': 'b'}
    
    markers = {
        'hold': 'o',
        'no-hold': 'x'
    }
    
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    
    for fluid, method_data in results.items():
        for method, ball_data in method_data.items():
            
            # data = results[fluid][method]['observed']['dimensional']
            # _add_to_plot(data, ax[0], label=f'{fluid} - {method} - observed', 
            #              fmt = markers[method], colour=colours[fluid])
            data = results[fluid][method]['fitted']['dimensional']
            _add_to_plot(data, ax[0], label=f'{fluid} - {method}', 
                         fmt = markers[method], colour=fitted_cmap[fluid], scale=100)
            # data = results[fluid][method]['observed']['non-dimensional']
            # _add_to_plot(data, ax[1], label=f'{fluid} - {method} - observed', 
            #              fmt = markers[method], colour=colours[fluid])
            data = results[fluid][method]['fitted']['non-dimensional']
            _add_to_plot(data, ax[1], label=f'{fluid} - {method}', 
                         fmt = markers[method], colour=fitted_cmap[fluid])
    ax[0].set_ylabel(r"$P_{th}$ (mbar)", fontsize=20)
    ax[1].set_ylabel(r"$P^*_{th}$", fontsize=20)
    #ax[0].set_title("Threshold pressure vs. ball diameter")
    
    ax[1].set_xlabel("Ball diameter (m)")
    
    handles, labels = plt.gca().get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax[0].legend(unique.values(), unique.keys(), framealpha=0, fontsize=20)
    ax[1].legend(unique.values(), unique.keys(), framealpha=0, fontsize=20)
    
    ax[0].grid(True, linestyle="--", alpha=0.3)
    ax[1].grid(True, linestyle="--", alpha=0.3)
    for axes in ax:
        axes.set_xlim(10, 19)
        axes.set_xlabel("Ball Diameter (mm)", fontsize=20)
        axes.set_xticks([11, 12, 14, 16, 18])
        axes.tick_params(labelsize=16)
    plt.tight_layout()
    if SAVE_FIG:
        plt.savefig(PLOTS_FOLDER/"thresholds.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    
    PRINT = True
    PLOT = True
    SAVE_FIG = True
    REDO = False
    if (not threshold_path.exists()) or REDO:
        get_thresholds()
    with open(threshold_path, "rb") as f:
        results = pickle.load(f)
    if PLOT:
        plot_threshold(results)
