
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 18:27:02 2025

@author: David Mawson 

Threshold Pressure
"""
from constants import BALL_DIAMETERS
from get_folderpaths import MASTER_FOLDER
from value_to_string import value_to_string
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
    
            for ball, p in ball_data.items():
                if ball not in BALL_DIAMETERS:
                    continue
    
                diam = BALL_DIAMETERS[ball]
                balls.append(ball)
                diameters.append(diam)
                pressures.append(p)
    
            if not balls:
                continue
    
            diameters = np.array(diameters)
            pressures = np.array(pressures)
            dimless_P, err = _get_dimless_pressure(pressures[:, 0], pressures[:, 1], diameters)
            
            data = np.column_stack((diameters, pressures))
            dimless_data = np.column_stack((diameters, dimless_P, err))
            save_dict[fluid][method]['observed']['dimensional'] = data
            save_dict[fluid][method]['observed']['non-dimensional'] = dimless_data

    with open(MASTER_FOLDER / "threshold_data.pkl", "wb") as f:
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

def _add_to_plot(data, ax, label, fmt, colour):
    # Plot with distinct colour + marker
    ax.errorbar(
        data[:, 0],
        data[:, 2],
        xerr=data[:, 1],
        yerr=data[:, 3],
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
        'oil': 'tab:green',
        'glycerol': 'tab:purple'}
    
    markers = {
        'hold': 'o',
        'no-hold': 'x'
    }
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    for fluid, method_data in results.items():
        for method, ball_data in method_data.items():
            
            data = results[fluid][method]['observed']['dimensional']
            _add_to_plot(data, ax[0], label=f'{fluid} - {method}', 
                         fmt = markers[method], colour=colours[fluid])
            data = results[fluid][method]['observed']['non-dimensional']
            _add_to_plot(data, ax[1], label=f'{fluid} - {method}', 
                         fmt = markers[method], colour=colours[fluid])
    plt.xlabel("Ball diameter (m)")
    plt.ylabel("Threshold pressure (mbar)")
    plt.title("Threshold pressure vs. ball diameter")
    
    handles, labels = plt.gca().get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    plt.legend(unique.values(), unique.keys())
    
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    if SAVE_FIG:
        plt.savefig(MASTER_FOLDER/"threshold_pressure.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    
    PRINT = True
    PLOT = True
    SAVE_FIG = True
    REDO = True
    if (not (MASTER_FOLDER / "threshold_data.pkl").exists()) or REDO:
        get_thresholds()
    with open(MASTER_FOLDER / "threshold_data.pkl", "rb") as f:
        results = pickle.load(f)
    if PLOT:
        plot_threshold(results)