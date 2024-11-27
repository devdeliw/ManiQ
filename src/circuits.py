from manim import *
from bisect import bisect_left, bisect_right
from typing import List, Set
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit

import ruamel.yaml as yaml 
import numpy as np
import pandas as pd
import math
import copy
import json


class Gates(Scene):
    """ 
        -- class for generating manim-space visuals
        -- for each type of quantum gate 
    """
    def construct(self):

        return

    def single(self, name, x, y, color=MAROON_D, params=[]):
        # -- generic single qubit gate
        # -- square visual
        label = MathTex(rf"{name}", font_size=55)

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
        border = Rectangle(
            width=label_group.width + 0.4,
            height=1,
            fill_color=color,
            fill_opacity=1,
            color=color,
        ).move_to([x, y, 0])

        label_group.move_to(border.get_center())
        gate = VGroup(border, label_group).move_to([x, y, 0])

        return gate

    def measure(self, x, y1, y2):
        # -- single qubit measurement gate
        # -- square measurement gate visual
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

        # -- vertical measurement lines to classical register(s)
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

        gate = VGroup(line_measure_1, line_measure_2, measure_tip, group)

        return gate

    def barrier(self, x, y1, y2): 
        # -- artificial barrier for aesthetic purposes 
        # -- and blocking off measurement gates 
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

        barrier = VGroup(rect, dotted_line)
        
        return barrier 

    # -- controlled pauli gates 
    # -- each with different design to match IBM Qiskit visual 
    def cx(self, x, y1, y2): 
        # -- control qubit 
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=BLUE_E,
        )
        # -- target qubit 
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

        # -- line connecting control & target qubits 
        line = Line(
                start=np.array([x, min(y1, y2), 0]), 
                end=np.array([x, max(y1, y2), 0]), 
                color=BLUE_E, 
                stroke_width=5,
        )
        gate = VGroup(line, control, target) 

        return gate 

    def cy(self, x, y1, y2): 
        # -- control qubit
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=MAROON_C,
        )
        # -- target qubit 
        target = self.single("Y", x, y2, color=MAROON_C)
        
        # -- line connecting control & target qubits 
        line = Line(
                start=np.array([x, min(y1, y2), 0]),
                end=np.array([x, max(y1, y2), 0]), 
                color=MAROON_C, 
                stroke_width=5
        )

        gate = VGroup(line, control, target) 

        return gate 

    # -- generic two-qubit control gate 
    def ctext(self, x, y1, y2, params=None): 
        # -- control qubit 
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=BLUE_C
        ) 
        # -- target qubit 
        target = Dot(
                point=np.array([x, y2, 0]), 
                radius=0.3,
                color=BLUE_C
        )
        # -- line connecting control & target qubits 
        line = Line(
                start=np.array([x, y1, 0]), 
                end=np.array([x, y2, 0]), 
                color=BLUE_C
        )

        # -- parameter label right of the qubit gates 
        if params: 
            y_param = min(y1, y2) + 1 
            if params[1]: 
                param_text = MathTex(rf"{params[0]} \; ({params[1][0]:.1f})", 
                                     font_size=40, 
                                     fill_color=WHITE,
                                     fill_opacity=1, 
                ).move_to([x+1, y_param, 0])
            else: 
                param_text = MathTex(rf"{params[0]}", 
                                     font_size=40, 
                                     fill_color=WHITE, 
                                     fill_opacity=1,
                ).move_to([x+0.5, y_param, 0])
            gate = VGroup(control, target, line, param_text) 
        else: 
            gate = VGroup(control, target, line) 

        return gate 

    def swap(self, x, y1, y2): 
        # -- generic two-qubit swap gate 
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

        # -- line connecting two qubits 
        line = Line(
                start=np.array([x, y1, 0]), 
                end=np.array([x, y2, 0]), 
                color=BLUE_E, 
                stroke_width=5,
        )
        gate = VGroup(cross1, cross2, line) 

        return gate 

    # general controlled-unitary gate 
    def cgate(self, name, x, y1, y2, color=MAROON_C, params=None): 
        # -- control qubit 
        control = Dot(
                point=np.array([x, y1, 0]), 
                radius=0.3, 
                color=color,
        )
        # -- target qubit 
        target = self.single(name, x, y2, color=color, params=params) 

        # -- line connecting control & target qubits 
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
        gate = VGroup(control, target, line) 
        
        return gate 

    def cswap(self, x, y1, y2, y3): 
        # -- controlled two-qubit swap gate
        # -- control qubit 
        control = Dot(
                point=np.array([x, y1, 0]),
                radius=0.3, 
                color=BLUE_E,
        )
        # -- target swap qubits
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

        # -- line in between 
        line = Line(
                start=np.array([x, min(y1,y2,y3), 0]), 
                end=np.array([x, max(y1,y2,y3), 0]), 
                color=BLUE_E, 
        )
        gate = VGroup(control, cross1, cross2, line) 

        return gate 

    # -- double controlled pauli gates 
    def ccx(self, x, y1, y2, y3): 
        # -- toffoli gate 
        # -- control qubits 
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
        # -- target qubit
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

        # -- line in between 
        line = Line(
                start=np.array([x, min(y1, y2, y3), 0]), 
                end=np.array([x, max(y1, y2, y3), 0]),
                color=BLUE_E, 
                stroke_width=5, 
        )
        gate = VGroup(line, control1, control2, target) 

        return gate 

    def ccz(self, x, y1, y2, y3): 
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

        # -- line in between 
        line = Line( 
                start=np.array([x, min(y1, y2, y3), 0]), 
                end=np.array([x, max(y1, y2, y3), 0]), 
                color=BLUE_C, 
                stroke_width=5,
        )
        gate = VGroup(line, dot1, dot2, dot3) 

        return gate

    def ccgate(self, name, x, y1, y2, y3, params=None):
        # -- general two-control-qubit controlled gate
        # -- control qubits 
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

        # -- target qubit 
        target = self.single(name, x, y3, params=params, color=MAROON_C) 

        # -- line in between 
        line = Line(
                start=np.array([x, min(y1, y2, y3), 0]), 
                end=np.array([x, max(y1, y2, y3), 0]), 
                stroke_width=5, 
                color=MAROON_C, 
        )
        gate = VGroup(line, control1, control2, target) 
        return gate 

    def cccgate(self, name, x, y1, y2, y3, y4, params=None): 
        # -- general three-control-qubit controlled gate 
        # -- control qubits
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
        # -- target qubits 
        target = self.single(name, x, y4, params=params, color=MAROON_C) 

        # -- line in between 
        line = Line(start=np.array([x, min(y1, y2, y3, y4), 0]), 
                    end=np.array([x, max(y1, y2, y3, y4), 0]), 
                    stroke_width=5, 
                    color=MAROON_C)
        gate = VGroup(line, control1, control2, control3, target)

        return gate 

    def multiqubit(self, name, x, y, color=MAROON_D, params=None, idxs=None): 
        # -- generic multi-qubit gate 
        label = MathTex(rf"{name}", font_size=60).move_to([x+0.5, np.mean(y), 0])
        group = VGroup(label) 

        if params:
            param_str = ", ".join([f"{param:.2f}" for param in params])
            param_str = MathTex(param_str, font_size=40).next_to(label, DOWN*1)
            group = VGroup(label, param_str) 

        rect = Rectangle(
                width=label.width+0.1, 
                height=label.height
        ).move_to(label.get_center())

        # -- logic to place gate idxs labels at correct wire 
        idxs_, y_ = VGroup(), y.copy() 
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

class Build(Scene): 
    """
        -- class to convert qiskit-space QuantumCircuit
        -- object into manim-space circuit visual 
    """ 
    def construct(self, qc): 
        return 

    def sort_instructions(self, qc):
        # -- logic to sort circuit instructions to ensure no overlap

        # -- assigns each gate a time-width of 1
        # -- sorts qubit gates based on their available start time

        # -- dict to store available qubit start times
        qubit_times = {i: 0 for i in range(qc.num_qubits)}
        # -- to store sorted QuantumCircuit instructions 
        sorted_instructions = []

        for instruction in qc.data:
            # -- qubits instruction acts on
            instruction_qubits = [qc.find_bit(qubit).index for qubit in instruction.qubits]
            min_qubit, max_qubit = min(instruction_qubits), max(instruction_qubits)

            # -- set gate start time as maximum start time for any qubit in between
            start_time = max(qubit_times[q] for q in range(min_qubit, max_qubit+1))
            sorted_instructions.append((start_time, instruction))

            # -- increases start time for all qubits
            # -- in collision of instruction gate
            for q in range(min_qubit, max_qubit+1):
                qubit_times[q] = start_time + 1

        sorted_instructions.sort(key=lambda q: q[0])
        self.sorted_instructions = sorted_instructions

        return

    def decompose(self, qc):
        # -- decomposes qiskit QuantumCircuit 
        # -- into sorted dataframe 
        
        try:
            with open('gates.yaml', 'r') as f:
                gate_params = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("The 'gates.yaml' file was not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing 'gates.yaml': {e}")

        # -- initialize list to store all instruction information 
        data_records = []

        for start_time, instruction in self.sorted_instructions:
            operation_name = instruction.operation.name
            instruction_params = gate_params.get(operation_name, {})

            # -- extract parameters
            category = instruction_params.get('category')
            latex = instruction_params.get('latex', operation_name)
            color = instruction_params.get('color', 'MAROON_C')

            # -- extract only floating point parameters 
            params = [
                param for param in instruction.operation.params
                if isinstance(param, (float, np.floating))
            ]

            # -- get qubit and clbit indices instruction acts on 
            qbits = [qc.find_bit(qubit).index for qubit in instruction.qubits]
            cbits = [qc.find_bit(clbit).index for clbit in instruction.clbits]

            # -- append the records as a dictionary
            data_records.append({
                'categories': category,
                'start_times': start_time,
                'names': latex,
                'colors': color,
                'params': params,
                'qbits': qbits,
                'cbits': cbits
            })

        # -- create the DataFrame from the list of dictionaries
        self.circuit_data = pd.DataFrame(data_records)

        # -- sort the DataFrame by start_time for better organization
        self.circuit_data.sort_values(by='start_times', inplace=True)
        self.circuit_data.reset_index(drop=True, inplace=True)

        return

    def build(self, qc, gap = 1):
        circuit_data = self.circuit_data 
        num_qubits = qc.num_qubits 

        # -- evenly spaced quantum wires centered around y=0
        wire_y_pos = np.arange(num_qubits-1, -num_qubits, -2)

        for time in range(max(circuit_data['start_times'])+1): 
            # -- filtering the df for each start time 
            filtered_df = circuit_data[circuit_data['start_times'] == time]

            # -- iterating through gates with identical start times 
            # -- they will be aligned in the same column 
            gates = [] 
            for _, elements in filtered_df.iterrows(): 
                category = elements['category']
                name = elements['name']
                color = elements['color'] 
                params = elements['params']
                qbits = elements['qubits']
                cbits = elements['cbits'] 

                y_value = wire_y_pos[qbits]
                gate_instance = Gates()
                if category == 'single_qubit_gate': 
                    gate = gate_instance.single(
                        name, 
                        x=0,
                        y=y_value[0],
                        color=color,
                        params=params
                    )

                if category == 'cx_like_gate': 
                    if hasattr(gate_instance, name.lower()): 
                        method = getattr(gate_instance, name.lower())
                        if callable(method): 
                            if name.lower() != 'barrier':
                                try: 
                                    gate = method(
                                            x=0, 
                                            y1=y_value[0], 
                                            y2=y_value[1]
                                    )
                                except TypeError as e: 
                                    print(f"Error calling method {name.lower()} -- {e}")
                            else: 
                                try: 
                                    gate = method( 
                                            x=0, 
                                            y1=min(y_value), 
                                            y2=max(y_value)
                                    )
                                except TypeError as e: 
                                    print(f"Error calling method {name.lower()} -- {e}")

                elif category == 'cphase_gate': 
                    gate = gate_instance.ctext(
                            x=0, 
                            y1=y_value[0], 
                            y2=y_value[1], 
                            params=[name,params]
                    )
                elif category == 'general_controlled_gate':
                    gate = gate_instance.cgate(
                            name=name, 
                            x=0, 
                            y1=y_value[0], 
                            y2=y_value[1],
                            params=params
                    )
                elif category == 'multi_qubit_gate': 
                    sorted_idxs = sorted(range(len(qbits)), key=lambda x: qbits[x])
                    gate = gate_instance.multiqubit( 
                            name=name, 
                            x=0, 
                            y=y_value, 
                            color=color,
                            params=params, 
                            idxs=sorted_idxs
                    )
                elif category == 'multi_controlled_gate': 
                    if name.lower() in ['ccx', 'ccy', 'ccz', 'cswap']:
                        if hasattr(gate_instance, name.lower()): 
                            method = getattr(gate_instance, name.lower()): 
                            if callable(method): 
                                try: 
                                    gate = method(
                                            x=0,
                                            y1=y_value[0], 
                                            y2=y_value[1], 
                                            y3=y_value[2]
                                    )
                                except TypeError as e: 
                                    print(f"Error calling method {name.lower()} -- {e}")
                    else: 
                        gate = gate_instance.cccgate(
                                name=name, 
                                x=0,
                                y1=y_value[0], 
                                y2=y_value[1], 
                                y3=y_value[2], 
                                y4=y_value[3],
                            params=params
                        )
                gates.append(gate)

















                







                


