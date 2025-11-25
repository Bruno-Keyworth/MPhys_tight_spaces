# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 21:59:52 2025

@author: David

written by chat gpt because thats alot of typing
"""
# ============================================================
# BALL PRESETS FOR ALL METHODS + FLUIDS + REPEATS + STRETCHED
# ============================================================

# -----------------------------
# 1. ALL BALLS (WITH REPEATS)
# -----------------------------

all_balls_no_hold_oil = [
    {'name': 'ball1', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball1_repeat', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball2', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball2_repeat', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball3', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball3_repeat', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball4', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball4_repeat', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball5', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball5_repeat', 'method': 'no-hold', 'fluid': 'oil'}
]

all_balls_hold_oil = [
    {'name': 'ball1', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball1_repeat', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball2', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball2_repeat', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball3', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball3_repeat', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball4', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball4_repeat', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball5', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball5_repeat', 'method': 'hold', 'fluid': 'oil'}
]

all_balls_no_hold_glycerol = [
    {'name': 'ball1', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball1_repeat', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball2', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball2_repeat', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball3', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball3_repeat', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball4', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball4_repeat', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball5', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball5_repeat', 'method': 'no-hold', 'fluid': 'glycerol'}
]

all_balls_hold_glycerol = [
    {'name': 'ball1', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball1_repeat', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball2', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball2_repeat', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball3', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball3_repeat', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball4', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball4_repeat', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball5', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball5_repeat', 'method': 'hold', 'fluid': 'glycerol'}
]

# -----------------------------------------
# 2. ALL BALLS — NO REPEATS
# -----------------------------------------

all_balls_no_repeat_no_hold_oil = [
    {'name': 'ball1', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball2', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball3', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball4', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball5', 'method': 'no-hold', 'fluid': 'oil'}
]

all_balls_no_repeat_hold_oil = [
    {'name': 'ball1', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball2', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball3', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball4', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball5', 'method': 'hold', 'fluid': 'oil'}
]

all_balls_no_repeat_no_hold_glycerol = [
    {'name': 'ball1', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball2', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball3', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball4', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball5', 'method': 'no-hold', 'fluid': 'glycerol'}
]

all_balls_no_repeat_hold_glycerol = [
    {'name': 'ball1', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball2', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball3', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball4', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball5', 'method': 'hold', 'fluid': 'glycerol'}
]

# -----------------------------------------
# 3. INDIVIDUAL BALL PRESETS
# (ballX, ballX_repeat, ballX_stretched_1.5)
# -----------------------------------------

def _ball_group(name, method, fluid):
    return [
        {'name': f'{name}', 'method': method, 'fluid': fluid},
        {'name': f'{name}_repeat', 'method': method, 'fluid': fluid},
        {'name': f'{name}_stretched_1.5', 'method': method, 'fluid': fluid},
    ]

# Create groups for ball1–ball5, each method/fluid
all_ball1_no_hold_oil        = _ball_group('ball1', 'no-hold', 'oil')
all_ball1_hold_oil           = _ball_group('ball1', 'hold', 'oil')
all_ball1_no_hold_glycerol   = _ball_group('ball1', 'no-hold', 'glycerol')
all_ball1_hold_glycerol      = _ball_group('ball1', 'hold', 'glycerol')

all_ball2_no_hold_oil        = _ball_group('ball2', 'no-hold', 'oil')
all_ball2_hold_oil           = _ball_group('ball2', 'hold', 'oil')
all_ball2_no_hold_glycerol   = _ball_group('ball2', 'no-hold', 'glycerol')
all_ball2_hold_glycerol      = _ball_group('ball2', 'hold', 'glycerol')

all_ball3_no_hold_oil        = _ball_group('ball3', 'no-hold', 'oil')
all_ball3_hold_oil           = _ball_group('ball3', 'hold', 'oil')
all_ball3_no_hold_glycerol   = _ball_group('ball3', 'no-hold', 'glycerol')
all_ball3_hold_glycerol      = _ball_group('ball3', 'hold', 'glycerol')

all_ball4_no_hold_oil        = _ball_group('ball4', 'no-hold', 'oil')
all_ball4_hold_oil           = _ball_group('ball4', 'hold', 'oil')
all_ball4_no_hold_glycerol   = _ball_group('ball4', 'no-hold', 'glycerol')
all_ball4_hold_glycerol      = _ball_group('ball4', 'hold', 'glycerol')

all_ball5_no_hold_oil        = _ball_group('ball5', 'no-hold', 'oil')
all_ball5_hold_oil           = _ball_group('ball5', 'hold', 'oil')
all_ball5_no_hold_glycerol   = _ball_group('ball5', 'no-hold', 'glycerol')
all_ball5_hold_glycerol      = _ball_group('ball5', 'hold', 'glycerol')

# -----------------------------------------
# 4. ALL STRETCHED (ONLY STRETCHED BALLS)
# -----------------------------------------

all_stretched_no_hold_oil = [
    {'name': 'ball1_stretched_1.5', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball2_stretched_1.5', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball3_stretched_1.5', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball4_stretched_1.5', 'method': 'no-hold', 'fluid': 'oil'},
    {'name': 'ball5_stretched_1.5', 'method': 'no-hold', 'fluid': 'oil'}
]

all_stretched_hold_oil = [
    {'name': 'ball1_stretched_1.5', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball2_stretched_1.5', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball3_stretched_1.5', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball4_stretched_1.5', 'method': 'hold', 'fluid': 'oil'},
    {'name': 'ball5_stretched_1.5', 'method': 'hold', 'fluid': 'oil'}
]

all_stretched_no_hold_glycerol = [
    {'name': 'ball1_stretched_1.5', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball2_stretched_1.5', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball3_stretched_1.5', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball4_stretched_1.5', 'method': 'no-hold', 'fluid': 'glycerol'},
    {'name': 'ball5_stretched_1.5', 'method': 'no-hold', 'fluid': 'glycerol'}
]

all_stretched_hold_glycerol = [
    {'name': 'ball1_stretched_1.5', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball2_stretched_1.5', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball3_stretched_1.5', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball4_stretched_1.5', 'method': 'hold', 'fluid': 'glycerol'},
    {'name': 'ball5_stretched_1.5', 'method': 'hold', 'fluid': 'glycerol'}
]

