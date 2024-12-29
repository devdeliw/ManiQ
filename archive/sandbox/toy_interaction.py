import pyautogui
import numpy as np
from manim import *
from manim.opengl import *

config.preview = True
config.write_to_movie = False
config.renderer = "opengl"

class InteractiveRadius(Scene):
    def construct(self):
        plane = NumberPlane()
        cursor_dot = Dot().move_to(3 * RIGHT + 2 * UP)
        red_circle = Circle(
            radius=np.linalg.norm(cursor_dot.get_center()),
            color=RED,
        )

        red_circle.add_updater(
            lambda mob: mob.become(
                Circle(
                    radius=np.linalg.norm(cursor_dot.get_center()),
                    color=RED,
                )
            )
        )

        self.play(Create(plane), Create(red_circle), FadeIn(cursor_dot))
        self.cursor_dot = cursor_dot 

        self.interactive_embed()

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key as pyglet_key
        if symbol == pyglet_key.G:
            # Convert global screen coords to Manim coords
            x_manim, y_manim = self.global_cursor_to_manim()

            print("Global screen coords:", pyautogui.position())
            print(f"Manim coords:        ({x_manim:.3f}, {y_manim:.3f})")

            self.play(self.cursor_dot.animate.move_to([x_manim, y_manim, 0]))

        super().on_key_press(symbol, modifiers)

    def global_cursor_to_manim(self):
        """ 
        Converts pixel coordinates of cursor to manim-space coordinates. 

        Assumes top --left-- of desktop screen is (0,0). Works on macOS. 

        """

        x_global, y_global = pyautogui.position()  
        x_win, y_win = self.renderer.window.position 

        x_local = x_global - x_win
        y_local = y_global - y_win  

        w_width = self.renderer.window.width
        w_height = self.renderer.window.height

        mw = config.frame_width
        mh = config.frame_height

        x_norm = x_local / w_width
        y_norm = 1 - (y_local / w_height)

        x_manim = x_norm * mw - mw / 2
        y_manim = y_norm * mh - mh / 2

        return x_manim, y_manim



class Test(Scene):
    def construct(self):
        plane = NumberPlane() 
        cursor_dot = Dot().move_to(3*RIGHT + 2*UP)
        red_circle = Circle( 
                radius=np.linalg.norm(cursor_dot.get_center()), 
                color=RED, 
        )
        red_circle.add_updater(
                lambda mob: mob.become(
                    Circle(
                        radius=np.linalg.norm(cursor_dot.get_center()), 
                        color=RED,
                    )
                )
        )

        self.play(Create(plane), Create(red_circle), FadeIn(cursor_dot))
        self.cursor_dot = cursor_dot 

        self.interactive_embed() 

    def on_key_press(self, symbol, modifiers): 
        from pyglet.window import key as pyglet_key 
        if symbol == pyglet_key.G: 
            self.play(
                    self.cursor_dot.animate.move_to(self.mouse_point.get_center())
            )
        super().on_key_press(symbol, modifiers) 
