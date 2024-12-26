from manim import * 
import numpy as np 
import math 


class Gates: 
    """
        Generates Manim-space visuals for each type of generic quantum gate.
    """

    def single(self, name, x, y, color=MAROON_D, params=[]): 
        """ 
        Builds a Generic Single-Qubit Gate in Manim-space.

        Args: 
            x, y (float): (x,y) Coordinates for gate.
            color (Manim color): Manim color of gate. Defaults to MAROON_D.
            params (array-like): Array containing gate parameters. 
        Returns: 
            The Manim Gate Mobject. 

        """

        # Gate Label (i.e. X, Y, Z, H) 
        label = MathTex(rf"{name}", font_size = 55)

        # Provided parameters, display them below the gate label
        if params:
            param_str = ", ".join([f"{param:.2f}" for param in params])
            param_label = MathTex(
                rf"{param_str}", 
                font_size=30 
            ).next_to(label, DOWN * 0.1)
            label.shift(UP * 0.1)
        else:
            param_label = MathTex(
                rf"0.00", 
                font_size=30
            ).set_opacity(0)

        label_group = VGroup(label, param_label)

        # Quantum Gate Visual 
        border = Rectangle(
            width=label_group.width + 0.4,
            height=1,
            fill_color=color,
            fill_opacity=1,
            color=color,
        ).move_to([x, y, 0])


        label_group.move_to(border.get_center())

        # Final Gate Mobject
        gate = VGroup(border, label_group).move_to([x, y, 0])

        return gate 

    def measure(self, x, y1, y2):

        """
        Builds the Quantum Measurement Gate Visual in Manim-space

        Args: 
            x (float): x-coordinate for gate placement.
            y1 (float): y-coordinate for the quantum-wire gate segment. 
            y2 (float): y-coordiante for the classical-wire gate segment.

        Returns: 
            The Manim Gate Mobject
        """

        # Mimicking the Standard Measurement Gate Visual
        dot = Dot(
            radius=0.05, 
            color=GRAY_D
        ).move_to([x, y1 - 0.1, 0])
        semicirc = (
            Arc(
                fill_opacity=0,
                angle=PI,
                stroke_width=2,
                color=GRAY_D,
            )
            .scale(0.35)
            .move_to(dot.get_center() + np.array([0, 0.1, 0]))
        )
        line = Line(
            dot.get_center(),
            np.array([x + 0.3, y1 + 0.3, 0]),
            stroke_width=2,
            color=GRAY_D,
        )
        square = Square(
            side_length=1,
            color=YELLOW_A,
            fill_color=YELLOW_A,
            fill_opacity=1,
        ).move_to([x, y1, 0])
        group = VGroup(square, dot, line, semicirc)

        # Vertical measurement lines to classical register(s)
        line_measure_1 = Line(
            np.array([x - 0.07, y1, 0]),
            np.array([x - 0.07, y2 + 0.4, 0]),
            stroke_width=2,
            color=YELLOW_A,
        )
        line_measure_2 = line_measure_1.copy().shift(RIGHT * 0.14)
        measure_tip = (
            Triangle(
                color=YELLOW_A,
                fill_color=YELLOW_A,
                fill_opacity=1,
            )
            .scale(0.3)
            .rotate(60 * DEGREES)
            .move_to([x, y2 + 0.4, 0])
        )

        # Final Gate Mobject
        gate = VGroup(line_measure_1, line_measure_2, measure_tip, group)

        return gate

    def barrier(self, x, y1, y2): 
        """
        Builds artificial circuit barrier for aesthetic purposes.

        Args: 
            x (float): x-coordinate of barrier. 
            y1 (float): Upper y-coordinate of barrier. 
            y2 (float): Lower y-coordinate of barrier.

        Returns: 
            The Manim Gate Mobject.

        """

        # Simple Vertical Barrier 
        rect = Rectangle(
                width=0.5, 
                height=abs(y2-y1)+1, 
                fill_color=GRAY_B, 
                fill_opacity=0.8, 
                stroke_width=0,
        ).move_to([x, min(y1, y2)+abs(y1-y2)/2, 0])

        min_y, max_y = min(y1, y2), max(y1, y2) 
        dotted_line = DashedLine(
                start=np.array([x, min_y-0.5, 0]), 
                end=np.array([x, max_y+0.5, 0]), 
                color=GRAY_E, 
                stroke_width=1.5, 
        )

        # Final Barrier Mobject
        barrier = VGroup(rect, dotted_line)
        
        return barrier 

    def cx(self, x, y1, y2): 
        """
        Builds Controlled Pauli-X Rotation Gate.

        Args: 
            x (float) : x-coordinate of gate 
            y1 (float): y-coordinate of control qubit.
            y2 (float): y-coordinate of target qubit

        Returns: 
            The Manim Gate Mobject.
        """
        # The Control Qubit 
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=BLUE_E,
        )
        # The Target Qubit 
        circle = Circle(
                radius=0.5, 
                color=BLUE_E, 
                fill_opacity=1,
        ).move_to([x, y2, 0]) 
        plus = VGroup(
            Line(
                start=np.array([x-0.3, y2, 0]), 
                end=np.array([x+0.3, y2, 0]), 
                stroke_width=2,
            ), 
            Line(
                start=np.array([x, y2-0.3, 0]), 
                end=np.array([x, y2+0.3, 0]), 
                stroke_width=2, 
            )
        )
        target = VGroup(circle, plus) 

        # Line connecting control & target qubits 
        line = Line(
                start=np.array([x, min(y1, y2), 0]), 
                end=np.array([x, max(y1, y2), 0]), 
                color=BLUE_E, 
                stroke_width=5,
        )
        
        # Final Gate Mobject
        gate = VGroup(line, control, target) 

        return gate 

    def cy(self, x, y1, y2): 
        # The Control Qubit
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=MAROON_C,
        )
        # THe Target Qubit 
        target = self.single("Y", x, y2, color=MAROON_C)
        
        # Line connecting control & target qubits 
        line = Line(
                start=np.array([x, min(y1, y2), 0]),
                end=np.array([x, max(y1, y2), 0]), 
                color=MAROON_C, 
                stroke_width=5
        )

        # Final Gate Mobject
        gate = VGroup(line, control, target) 

        return gate 

    # Generic two-qubit control gate 
    def ctext(self, x, y1, y2, params=None): 
        """
        Builds a Generic Two-Qubit Controlled Gate. 
        
        Args: 
            x (float): x-coordinate of gate. 
            y1 (float): y-coordinate of control qubit. 
            y2 (float): y-coordinate of target qubit. 
            params (array-like): Contains parameters for gate. 
                                 Placed beside Gate.

        Returns: 
            The Manim Gate Mobject.
        """
        # Control Qubit 
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=BLUE_C
        ) 
        # Target Qubit 
        target = Dot(
                point=np.array([x, y2, 0]), 
                radius=0.3,
                color=BLUE_C
        )
        # Line connecting control & target qubits 
        line = Line(
                start=np.array([x, y1, 0]), 
                end=np.array([x, y2, 0]), 
                color=BLUE_C
        )

        # Parameter label beside gate 
        if params:
            y_param = min(y1,y2)-0.7 
            if params[1]: 
                param_text = MathTex(rf"{params[0]} \; ({params[1][0]:.2f})", 
                                     font_size=40, 
                                     fill_color=WHITE,
                                     fill_opacity=1, 
                ).move_to([x, y_param, 0])
            else: 
                param_text = MathTex(rf"{params[0]}", 
                                     font_size=40, 
                                     fill_color=WHITE, 
                                     fill_opacity=1,
                ).move_to([x, y_param, 0])
            # Final Gate Mobject
            gate = VGroup(control, target, line, param_text)
        else: 
            # Final Gate Mobject
            gate = VGroup(control, target, line) 

        return gate 

    def swap(self, x, y1, y2): 
        """ 
        Builds Generic Two-Qubit SWAP Gate. 
        
        Args: 
            x (float): x-coordinate of gate.
            y1 (float): Upper y-coordinate of gate. 
            y2 (float): Lower y-coordinate of gate. 
        
        Returns: 
            The Manim Gate Mobject. 

        """

        # SWAP Gate Visual 
        cross1 = Cross(
                stroke_color=BLUE_E, 
                scale_factor=0.4, 
                stroke_width=4,
        ).move_to([x, y1, 0])
        cross2 = Cross(
                stroke_color=BLUE_E, 
                scale_factor=0.4, 
                stroke_width=4,
        ).move_to([x, y2, 0])

        # Line connecting two qubits 
        line = Line(
                start=np.array([x, y1, 0]), 
                end=np.array([x, y2, 0]), 
                color=BLUE_E, 
                stroke_width=5,
        )

        # Final Gate Mobject
        gate = VGroup(cross1, cross2, line) 

        return gate 

    # general controlled-unitary gate 
    def cgate(self, name, x, y1, y2, color=MAROON_C, params=None): 
        """ 
        Builds General Controlled-Unitary Gate. 

        Args: 
            name (str): Name of the Unitary Gate Label.
            x (float): x-coordinate of gate. 
            y1 (float): y-coordinate of control qubit. 
            y2 (float): y-coordinate of target qubit. 
            color (Manim color): Color of gate. 
            params (array-like): Parameters of gate. 
                                 Placed below Gate Label.

        Returns: 
            The Manim Gate Mobject.

        """    
        # Control Qubit 
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=color,
        )
        # Target Qubit 
        target = self.single(name, x, y2, color=color, params=params) 

        # Line connecting control & target qubits 
        if y2 < y1:
            end = np.array([x, y2+0.5, 0]) 
        else: 
            end = np.array([x, y2-0.5, 0]) 

        line = Line(
                start=np.array([x, y1, 0]), 
                end=end, 
                stroke_width=5, 
                color=color, 
        )

        # Final Gate Mobject
        gate = VGroup(control, target, line) 
        
        return gate 

    def cswap(self, x, y1, y2, y3): 
        """ 
        Builds Controlled Two-Qubit Swap Gate.

        Args: 
            x: x-coordinate of gate.
            y1: y-coordinate of control qubit. 
            y2: y-coordinate of target qubit 1. 
            y3: y-coordinate of target qubit 2. 

        Returns: 
            The Manim Gate Mobject. 

        """

        # Control Qubit 
        control = Dot(
                point=np.array([x, y1, 0]),
                radius=0.3, 
                color=BLUE_E,
        )
        # Target SWAP Qubits
        cross1 = Cross(
                stroke_color=BLUE_E, 
                scale_factor=0.4, 
                stroke_width=4,
        ).move_to([x, y2, 0])
        cross2 = Cross(
                stroke_color=BLUE_E, 
                scale_factor=0.4, 
                stroke_width=4,
        ).move_to([x, y3, 0])

        # Line in between 
        line = Line(
                start=np.array([x, min(y1,y2,y3), 0]), 
                end=np.array([x, max(y1,y2,y3), 0]), 
                color=BLUE_E, 
        )

        # Final Gate Mobject
        gate = VGroup(control, cross1, cross2, line) 

        return gate 

    def ccx(self, x, y1, y2, y3): 
        """
        Builds Double-Controlled Pauli X Rotation Gate. 

        Args: 
            x (float): x-coordinate of gate.
            y1 (float): y-coordinate of 1st control qubit.
            y2 (float): y-coordinate of 2nd control qubit. 
            y3 (float): y-coordinate of target qubit. 

        Returns: 
            The Manim Gate Mobject. 

        """   
        # Toffoli Gate 
        # Control Qubits 
        control1 = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=BLUE_E,
        )
        control2 = Dot(
                point=np.array([x, y2, 0]), 
                radius=0.3, 
                color=BLUE_E, 
        )
        # Target Qubit
        circle = Circle(
                radius=0.5, 
                color=BLUE_E, 
                fill_opacity=1,
        ).move_to([x, y3, 0])
        plus = VGroup( 
            Line(
                start=np.array([x-0.3, y3, 0]), 
                end=np.array([x+0.3, y3, 0]), 
                stroke_width=2,
            ),
            Line(
                start=np.array([x, y3-0.3, 0]), 
                end=np.array([x, y3+0.3, 0]), 
                stroke_width=2, 
            )
        )
        target = VGroup(circle, plus) 

        # Line in between 
        line = Line(
                start=np.array([x, min(y1, y2, y3), 0]), 
                end=np.array([x, max(y1, y2, y3), 0]),
                color=BLUE_E, 
                stroke_width=5, 
        )

        # Final Gate Mobject
        gate = VGroup(line, control1, control2, target) 

        return gate 

    def ccz(self, x, y1, y2, y3):
        """ 
        Builds Symmetric Toffoli-Z Gate. 

        Args: 
            x (float): x-coordinate of gate. 
            y1 (float): y-coordinate of qubit 1. 
            y2 (float): y-coordinate of qubit 2. 
            y3 (float): y-coordinate of qubit 3.

        Returns: 
            The Manim Gate Mobject.

        """
        # Three Qubits
        dot1 = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=BLUE_C, 
        )
        dot2 = Dot(
                  point=np.array([x, y2, 0]),
                  radius=0.3,
                  color=BLUE_C,
        )
        dot3 = Dot(
                  point=np.array([x, y3, 0]),
                  radius=0.3,
                  color=BLUE_C,
        )

        # Line in between 
        line = Line( 
                start=np.array([x, min(y1, y2, y3), 0]), 
                end=np.array([x, max(y1, y2, y3), 0]), 
                color=BLUE_C, 
                stroke_width=5,
        )

        # Final Gate Mobject
        gate = VGroup(line, dot1, dot2, dot3) 

        return gate

    def ccgate(self, name, x, y1, y2, y3, params=None):
        """
        Builds Generalized Two-Control-Qubit Gate.

        Args: 
            name (str): Name for gate label.
            x (float): x-coordinate of gate. 
            y1 (float): y-coordinate of 1st control qubit. 
            y2 (float): y-coordinate of 2nd control qubit. 
            y3 (float): y-coordinate of target qubit. 
            params (array-like): Parameters for control gate.

        Returns: 
            The Manim Gate Mobject.

        """    
        # Control Qubits 
        control1 = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3,
                color=MAROON_C, 
        )
        control2 = Dot(
                point=np.array([x, y2, 0]), 
                radius=0.3, 
                color=MAROON_C, 
        )

        # Target Qubit 
        target = self.single(name, x, y3, params=params, color=MAROON_C) 

        # Line in between 
        line = Line(
                start=np.array([x, min(y1, y2, y3), 0]), 
                end=np.array([x, max(y1, y2, y3), 0]), 
                stroke_width=5, 
                color=MAROON_C, 
        )

        # Final Gate Mobject
        gate = VGroup(line, control1, control2, target) 

        return gate 

    def cccgate(self, name, x, y1, y2, y3, y4, params=None): 

        """ 
        Builds Generalized Three-Control-Qubit Gate. 
        Args: 
            name (str): Name for gate label.
            x (float): x-coordinate of gate. 
            y1 (float): y-coordinate of 1st control qubit. 
            y2 (float): y-coordinate of 2nd control qubit. 
            y3 (float): y-coordinate of 3rd control qubit. 
            y4 (float): y-coordinate of target qubit.
            params (array-like): Parameters for control gate.

        Returns: 
            The Manim Gate Mobject.

        """

        # Control Qubits
        control1 = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=MAROON_C, 
        )
        control2 = Dot(
                  point=np.array([x, y2, 0]),
                  radius=0.3,
                  color=MAROON_C,
        )
        control3 = Dot(
                  point=np.array([x, y3, 0]),
                  radius=0.3,
                  color=MAROON_C,
        )

        # Target Qubit
        target = self.single(name, x, y4, params=params, color=MAROON_C) 

        # Line in between 
        line = Line(start=np.array([x, min(y1, y2, y3, y4), 0]), 
                    end=np.array([x, max(y1, y2, y3, y4), 0]), 
                    stroke_width=5, 
                    color=MAROON_C)

        # Final Gate Mobject
        gate = VGroup(line, control1, control2, control3, target)

        return gate 

    def multiqubit(self, name, x, y, color=MAROON_D, params=None, idxs=None): 
        """ 
        Builds Generalized Multi-Qubit Gate. 

        Args: 
            name (str): Name for gate label.
            x (float): x-coordinate for gate. 
            y (array-like): y-coordinates for qubits being acted on. 
            color (Manim color): Color for gate. Defaults to MAROON_D. 
            params (array-like): Contains parameters for gate. 
                                 Placed below gate label. 
            idxs (array-like): Stores index positions from top-to-bottom 
                               that identify which qubits are acted on. 
                               Mimicks IBM Qiskit's visuals. 
        Returns: 
            The Manim Gate Mobject. 

        """

        # Gate Label
        label = MathTex(rf"{name}", font_size=60).move_to([x+0.5, np.mean(y), 0])
        group = VGroup(label) 

        # Gate Parameters 
        # Placed below Gate Label
        if params:
            param_str = ", ".join([f"{param:.2f}" for param in params])
            param_str = MathTex(param_str, font_size=40).next_to(label, DOWN*1)
            group = VGroup(label, param_str) 

        rect = Rectangle(
                width=label.width+0.1, 
                height=label.height
        ).move_to(label.get_center())

        # Logic to place gate idxs labels at correct qubit wire(s) 
        idxs_, y_ = VGroup(), list(y.copy())
        if idxs: 
            for i in range(len(idxs)): 
                idx = MathTex(
                        rf"{idxs[i]}", 
                        font_size=60, 
                ).move_to([x-0.3, max(y_), 0])
                idxs_.add(idx)
                y_.remove(max(y_)) 
        idxs_.next_to(rect, LEFT) 
        group = VGroup(group, idxs_) 

        # Final Gate Mobject
        gate = VGroup(
            Rectangle(
                width=group.width+0.3, 
                height=math.ceil(group.height+0.4), 
                fill_color=color, 
                color=color, 
                fill_opacity=1,
            ).move_to(group.get_center()), 
            group
        ).move_to([x, np.mean(y), 0])

        return gate

