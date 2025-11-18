
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 18:27:02 2025

@author: David Mawson 

Threshold Pressure
"""
from constants import BALL_DIAMETERS
from get_folderpaths import MASTER_FOLDER
import numpy as  np
import matplotlib.pyplot as plt


import os
import re
from collections import defaultdict


pressure_pattern = re.compile(r"(\d+)\s*mbar", re.IGNORECASE)
ball_base_pattern = re.compile(r"(ball\d+)")  # captures ball1 from ball1_repeat

def get_results():

    results = defaultdict(lambda: defaultdict(dict))
    
    for fluid in os.listdir(MASTER_FOLDER):
        fluid_path = os.path.join(MASTER_FOLDER, fluid)
        if not os.path.isdir(fluid_path):
            continue
    
        for method in os.listdir(fluid_path):
            method_path = os.path.join(fluid_path, method)
            if not os.path.isdir(method_path):
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
                avg_lowest_pressure = sum(values) / len(values)
                results[fluid][method][base_ball_name] = avg_lowest_pressure
    return results


def print_results(results):
    if PRINT:
        for fluid, method_data in results.items():
            print(f"\n=== {fluid.upper()} ===")
            for method, ball_data in method_data.items():
                print(f"  -- {method} --")
                for ball, p in ball_data.items():
                    print(f" {ball}: lowest averaged pressure = {p:.2f} mbar")

def plot_threshold(results):
    colour_map = {
    'oil': 'tab:red',
    'glycerol': 'tab:blue'
    }
    
    marker_map = {
        'hold': 'o',
        'no-hold': 'x'
    }
    
    pressure_err = 10  # mbar uncertainty
    
    plt.figure(figsize=(10, 6))
    
    for fluid, method_data in results.items():
        for method, ball_data in method_data.items():
    
            balls = []
            diameters = []
            diameter_errs = []
            pressures = []
    
            for ball, p in ball_data.items():
                if ball not in BALL_DIAMETERS:
                    continue
    
                diam, diam_err = BALL_DIAMETERS[ball]
                balls.append(ball)
                diameters.append(diam)
                diameter_errs.append(diam_err)
                pressures.append(p)
                
                
    
            if not balls:
                continue
    
            diameters = np.array(diameters)
            diameter_errs = np.array(diameter_errs)
            pressures = np.array(pressures)
            pressure_errs = np.zeros(len(pressures)) + pressure_err
            
            data = np.column_stack((diameters, pressures, diameter_errs, pressure_errs))
            np.savetxt(MASTER_FOLDER / fluid/method/'threshold_data.txt', data)
            
            # Plot with distinct colour + marker
            plt.errorbar(
                diameters,
                pressures,
                xerr=diameter_errs,
                yerr=pressure_err,
                fmt=marker_map[method],
                color=colour_map[fluid],
                ecolor='black',
                elinewidth=1,
                capsize=3,
                label=f"{fluid} – {method}"
            )
    
    plt.xlabel("Ball diameter (m)")
    plt.ylabel("Threshold pressure (mbar)")
    plt.title("Threshold pressure vs. ball diameter")
    
    handles, labels = plt.gca().get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    plt.legend(unique.values(), unique.keys())
    
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    if SAVE_FIG:
        plt.savefig(MASTER_FOLDER//"threshold_pressure.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    
    PRINT = True
    PLOT = True
    SAVE_FIG = False

    results = get_results()
    if PLOT:
        plot_threshold(results)
    
    if PRINT:
        print_results(results)