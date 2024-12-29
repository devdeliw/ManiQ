from manim import *

import pyautogui 
import numpy as np 

""" 
Helper Functions for configuring user interactions 

""" 

def global_cursor_to_manim(scene, scaling_factor):
    """ 
    Converts pixel coordinates of cursor to manim-space coordinates. 

    Assumes top --left-- of desktop screen is (0,0). Works on 
    most modern OS.

    """

    # Global cursor positions
    x_global, y_global = pyautogui.position() 

    # Top-left pyglet window position
    x_win, y_win = scene.renderer.window.position 

    # Local coords within pyglet window
    x_local = x_global - x_win
    y_local = y_global - y_win

    # Width of pyglet window
    w_width = scene.renderer.window.width 
    w_height = scene.renderer.window.height

    # Manim system dimensions
    mw = config.frame_width * scaling_factor
    mh = config.frame_height * scaling_factor

    # Normalizing to within pyglet window
    x_norm = x_local / w_width
    # 1 - is because pyglet window increases y from bottom-up
    y_norm = 1 - (y_local / w_height)

    # Final manim-space cursor coordinates
    x_manim = x_norm * mw - mw / 2
    y_manim = y_norm * mh - mh / 2
    return x_manim, y_manim



def get_bounding_box(mobj): 
    """
    Gets the live bounding box in manim-space for a mobject. 
    Not using an updater cause a calculation is needed only 
    whenever the given mobject *moves*. 

    """

    # Numerically calculate min, max coords using mobj points  
    all_points = [] 
    for sub in mobj.family_members_with_points(): 
        all_points.append(sub.points) 
    if not all_points: 
        return None 

    all_points = np.vstack(all_points) 
    min_vals = all_points.min(axis=0) 
    max_vals = all_points.max(axis=0) 
    return([min_vals, max_vals]) # lower left & upper right coords
