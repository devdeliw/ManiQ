from manim import * 
from manim.opengl import * 

config.preview = True 
config.write_to_movie = False 

""" Just testing how manims frame dimensions work """

class FrameDimensions(Scene):
    def construct(self):
        self.mw = config.frame_width 
        self.mh = config.frame_height 

        self.line1 = Line(self.mw * LEFT/2, self.mw * RIGHT/2).to_edge(DOWN)
        self.line2 = Line(self.mh * UP/2, self.mh * DOWN/2).to_edge(LEFT) 

        self.play(Write(self.line1), Write(self.line2))
        self.interactive_embed()
        return 

    def adjust_frame(self, scaling_factor):
        self.mw = self.mw * scaling_factor 
        self.mh = self.mh * scaling_factor

        newline1 = Line(self.mw * LEFT/2, self.mw * RIGHT/2, color=BLUE).to_edge(DOWN)
        newline2 = Line(self.mh * UP/2, self.mh * DOWN/2, color=BLUE).to_edge(LEFT)

        self.play(ReplacementTransform(self.line1, newline1))
        self.play(ReplacementTransform(self.line2, newline2)) 

        self.line1 = newline1 
        self.line2 = newline2 

        print(self.mw, self.mh)
        return 


