from manim import * 
from manim.opengl import *

from toy_interaction import InteractiveRadius

import pyautogui 
import numpy as np 

config.preview = True 
config.write_to_movie = False 
config.renderer='opengl' 

def global_cursor_to_manim(scene, scaling_factor):
    """ 
    Converts pixel coordinates of cursor to manim-space coordinates. 

    Assumes top --left-- of desktop screen is (0,0). Works on macOS. 

    """

    print(scene.renderer)

    x_global, y_global = pyautogui.position()  
    x_win, y_win = scene.renderer.window.position 

    x_local = x_global - x_win
    y_local = y_global - y_win  

    w_width = scene.renderer.window.width 
    w_height = scene.renderer.window.height

    mw = config.frame_width * scaling_factor
    mh = config.frame_height * scaling_factor

    x_norm = x_local / w_width
    y_norm = 1 - (y_local / w_height)

    x_manim = x_norm * mw - mw / 2
    y_manim = y_norm * mh - mh / 2

    return x_manim, y_manim

class MouseScene(Scene): 
    def construct(self): 
        self.circle = Circle(color=BLUE) 
        self.play(Write(self.circle)) 
        self.interactive_embed()
        
    def on_mouse_drag(self, point, d_point, buttons, modifiers): 
        new_radius = np.linalg.norm(point) 
        self.circle.become(
            Circle(
                color=BLUE, 
                radius=new_radius, 
                fill_opacity=0.5 * abs(np.sin(new_radius)), 
            )
        )

class BoundingBox(Scene):
    """ 
    Testing to see Manim interactivity with mouse clicks 

    """

    def construct(self): 
        self.square = Square(side_length=3, fill_opacity = 1, color=MAROON_C) 
        self.play(Write(self.square))
        self.interactive_embed() 

    def on_mouse_press(self, point, button, modifiers): 
        self.square.get_corner(DL)

        # lower left corner and upper right corner manim coordinates 
        # of square mobject
        bbox = np.array(
                [self.square.get_corner(DL), self.square.get_corner(UR)]
        )

        x_manim, y_manim = global_cursor_to_manim(self, 1.5) 

        if bbox[0,0] <= x_manim <= bbox[1,0]:
            if bbox[0,1] <= y_manim <= bbox[1,1]: 
                print('mouse inside square')
        else: 
            print('mouse outside square')

        super().on_mouse_press(point, button, modifiers) 





