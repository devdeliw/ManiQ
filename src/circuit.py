from manim import * 
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
import numpy as np
import pandas as pd
import json


class Gates(Scene):
    def construct(self):

        ctext = self.cgate('CU1', 0, 1, -1, color = 'BLUE_D')  
        self.add(ctext)

    # default single qubit gates
    def single(self, name, x, y, color = MAROON_D, params=[]):
        label = MathTex(rf"{name}", font_size=55)

        if params:
            param_str = ", ".join([f"{param:.2f}" for param in params])
            label2 = MathTex(rf"{param_str}", font_size=30).next_to(label, DOWN * 0.1)
            label.shift(UP * 0.1)  
        else:
            label2 = MathTex(rf"0.00", font_size=30).set_opacity(0)  

        label_group = VGroup(label, label2)
        border = Rectangle(width=label_group.width+0.4, height=1,
                           fill_color=color, fill_opacity=1, 
                           color=color).move_to([x, y, 0])
        label_group.move_to(border.get_center())
        gate = VGroup(border, label_group).move_to([x, y, 0])

        return gate


    def measurement(self, x, y): 
        # measurement qubit
        dot = Dot(radius = 0.05).move_to([x, y-0.1, 0])
        semicirc = Arc(fill_opacity=0,
                       angle=PI, 
                       stroke_width = 7).scale(0.35).move_to(np.add(
                           dot.get_center(), np.array([0, 0.1, 0])))
        line = Line(dot.get_center(), 
                    np.array([x + 0.3, y + 0.3, 0]),
                    stroke_width = 5)
        square = Square(side_length = 1).move_to([x, y, 0])
        group = VGroup(dot, semicirc, line, square)

        return group

    # controlled pauli gates
    # each has a different design 
    def cx(self, x1, y1, y2):
        # control qubit
        dot = Dot(point = np.array([x1, y1, 0]), 
                  radius = 0.15, 
                  color = BLUE_D)
        # target qubit 
        circle = Circle(radius = 0.5, 
                        color = BLUE_D, 
                        fill_opacity = 1).move_to([x1, y2, 0]) 
        plus = VGroup(
                Line(start = np.array([x1- 0.3, y2, 0]), 
                     end = np.array([x1+ 0.3, y2, 0]),
                     stroke_width = 5), 
                Line(start = np.array([x1, y2 - 0.3, 0]),
                     end = np.array([x1, y2 + 0.3, 0]),
                     stroke_width = 5))
        circle = VGroup(circle, plus)

        # line in between   
        if y2 < y1: 
            end = np.array([x1, y2 + 0.5, 0])
        else: 
            end = np.array([x1, y2 - 0.5, 0])

        line = Line(start = np.array([x1, y1, 0]), 
                    end = end, 
                    color = BLUE_D,
                    stroke_width = 5)

        gate = VGroup(dot, circle, line) 
        return gate

    def cy(self, x1, y1, y2): 
        # control qubit
        dot = Dot(point = np.array([x1, y1, 0]),
                  radius = 0.15,
                  color = MAROON_C)
        # target qubit
        target = self.single("Y", x1, y2, color=MAROON_C)

        # line in between
        if y2 < y1:
            end = np.array([x1, y2 + 0.5, 0])
        else:
            end = np.array([x1, y2 - 0.5, 0])

        line = Line(start = np.array([x1, y1, 0]),
                    end = end,
                    color = MAROON_C,
                    stroke_width = 5)

        gate = VGroup(dot, target, line)
        return gate
    
    def ctext(self, x1, y1, y2, params = None): 
        # control qubit 
        dot1 = Dot(point = np.array([x1, y1, 0]), 
                  radius = 0.15, 
                  color = BLUE_B) 
        # target qubit
        dot2 = Dot(point = np.array([x1, y2, 0]),
                  radius = 0.15, 
                  color = BLUE_B)
        # line in between 
        line = Line(start = np.array([x1, y1, 0]), 
                    end = np.array([x1, y2, 0]), 
                    color = BLUE_B)

        if params: 
            param_text = MathTex(rf"{params[0]} \; {params[1][0]:.2f}",
                                 font_size = 30).move_to(
                                         [x1+0.9, min(y1, y2) + abs(y2-y1)/2, 0])
            gate = VGroup(dot1, dot2, line, param_text)
        else: 
            gate = VGroup(dot1, dot2, line)

        return gate 

    # general controlled unitary gate
    def cgate(self, name, x1, y1, y2, color = MAROON_D, params = None): 
        # control qubit
        dot = Dot(point=np.array([x1, y1, 0]),
                  radius=0.15, color=color)
        label = MathTex(rf"{name}", font_size = 80)

        if params: 
            param_text = MathTex(rf"{params}", 
                                 font_size = 40).next_to(label, DOWN)
            label = VGroup(label, param_text)

        target = self.single(name, x1, y2, 
                             color=color)

        # line in between
        if y2 < y1:
            end = np.array([x1, y2 + 0.5, 0])
        else:
            end = np.array([x1, y2 - 0.5, 0])

        line = Line(start=np.array([x1, y1, 0]),
                    end=end,
                    stroke_width=5, 
                    color=color)

        gate = VGroup(dot, target, line)
        return gate

    def multi(self, name, x1, y1, y2, color = MAROON_D, params = None, idxs = None): 
        # gate spanning multiple qubits
        label = MathTex(rf"{name}", 
                        font_size = 60).move_to([x1+0.5, min(y1,y2) + abs(y1-y2) / 2, 0])

        group = VGroup(label)

        if params: 
            param_str = ", ".join([f"{param:.2f}" for param in params])
            param_str = MathTex(param_str, 
                                font_size = 40).next_to(label, DOWN*1)
            group = VGroup(label, param_str)
        group_rect = Rectangle(width=label.width + 0.1,
                               height=label.height, 
                               color = color).move_to(label.get_center())
        if idxs: 
            idx1 = MathTex(rf"{idxs[0]}",
                           font_size = 60).move_to([x1-0.3, max(y1, y2), 0])
            idx2= MathTex(rf"{idxs[1]}", 
                           font_size = 60).move_to([x1-0.3, min(y1, y2), 0])
            idxs_ = VGroup(idx1, idx2) 
            idxs_.next_to(group_rect, LEFT)
            group = VGroup(group, idxs_)

        gate = VGroup(
                Rectangle(
                    width=group.width + 0.3,
                    height=3, 
                    color = MAROON_E).move_to(group.get_center()),
                group).move_to(label.get_center())
        return gate

class BuildCircuit(Scene):
    def construct(self, qc, run_time = 5):

        mobjects = self.build(qc)
        circuit = VGroup(*mobjects)
        self.play(Write(circuit), run_time = run_time)

        return 

    def decompose(self, qc): 
        with open('gates.json', 'r') as file:
            quantum_gates = json.load(file)

        def categorize_gate(gate_name):
            gate_name = gate_name.lower()
            for category, gates in quantum_gates.items():
                for gate in gates:
                    if gate_name == gate['name']:
                        return category, gate['latex']

        categories, names, params, idxs = [], [], [], []
        for instruction in qc.data:
            category, latex = categorize_gate(instruction.operation.name)

            categories.append(category)
            names.append(latex)
            params.append([i for i in instruction.operation.params if isinstance(i, np.float64)])
            idxs.append([qc.find_bit(qubit).index for qubit in instruction.qubits])

        print(names)

        circuit_data = pd.DataFrame({
            'category': categories,
            'names': names,
            'params': params,
            'idxs': idxs
        })

        return circuit_data

    def build(self, qc):
        circuit_data = self.decompose(qc)
        mobjects = []

        q0x = -3
        q1x = -3
        for idx, elements in circuit_data.iterrows():
            category, name = elements.iloc[0], elements.iloc[1]
            params, qubits = elements.iloc[2], elements.iloc[3]

            if len(qubits) > 1:
                x = max(q0x, q1x)
                if qubits == [0, 1]: 
                    y1, y2 = 1, -1
                else: 
                    y1, y2 = -1, 1
            else:
                if qubits == [0]:
                    x, y = q0x, 1
                if qubits == [1]:
                    x, y = q1x, -1

            gate = VGroup()
            if category == 'single_qubit_gates': 
                gate = Gates().single(name, x=x, y=y, params=params)
                mobjects.append(gate)
            if category == 'cx_like_gates':
                if name.lower() == 'cx' or name.lower() == 'cnot':
                    gate = Gates().cx(x, y1, y2)
                    mobjects.append(gate) 
                if name.lower() == 'cy': 
                    gate = Gates().cx(x, y1, y2)
                    mobjects.append(gate)
                if name.lower() == 'cz': 
                    gate = Gates().ctext(x, y1, y2)
                    mobjects.append(gate)
            if category == 'cphase_gates': 
                gate = Gates().ctext(x, y1, y2, params=[name, params])
                mobjects.append(gate)
            if category == 'general_controlled_gates':
                gate = Gates().cgate(name, x, y1, y2, params=params)
                mobjects.append(gate)
            if category == 'multi_qubit_gates': 
                gate = Gates().multi(name, x, y1, y2, 
                                     params=params,idxs=qubits)
                mobjects.append(gate) 

            if len(qubits) > 1: 
                q0x += gate.width + 0.8
                q1x += gate.width + 0.8
            elif qubits == [0]: q0x += gate.width + 0.8
            elif qubits == [1]: q1x += gate.width + 0.8

        q0wire = Line(start=np.array([-5, 1, 0]),
                      end=np.array([max(q0x, q1x), 1, 0]),
                      stroke_width = 8)
        q1wire = Line(start=np.array([-5, -1, 0]), 
                      end=np.array([max(q0x, q1x), -1, 0]), 
                      stroke_width = 8)

        mobjects.append(q0wire)
        mobjects.append(q1wire)

        return mobjects


if __name__ == "__main__": 
    qc = random_circuit(2, max_operands = 2, depth = 4, seed = 25)
    print(qc)

    config.pixel_height = 480  # Set pixel height for low resolution
    config.pixel_width = 854    # Set pixel width for low resolution

    build_circuit_scene = BuildCircuit() 
    build_circuit_scene.construct(qc)







