from manim import * 
from manim.opengl import * 

config.preview = True 
config.write_to_movie = False 

class UpdaterBbox(Scene):
    def construct(self):
        square = Square(side_length=2).move_to([0, 0, 0])
        self.play(Write(square))
        self.interactive_embed()

    def get_bounding_box(mobj):
        all_points = []
        for sub in mobj.family_members_with_points():
            all_points.append(sub.points)
        if not all_points:
            return None

        all_points = np.vstack(all_points)  
        min_vals = all_points.min(axis=0)   # [min_x, min_y, min_z]
        max_vals = all_points.max(axis=0)   # [max_x, max_y, max_z]
        return [min_vals, max_vals]









