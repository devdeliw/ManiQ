from manim import * 
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
import numpy as np
import pandas as pd
import math
import copy
import json


class Gates(Scene):
    def construct(self):

        ctext = self.multi('CU1', 0, 1, -3, color = 'BLUE_D', idxs = [0, 1],
                           params = [1, 0])
        ctext = self.barrier(0, 2, 1)
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

    def measure(self, x, y1, y2): 
        # measurement qubit
        dot = Dot(radius=0.05,
                  color=GRAY_D).move_to([x, y1-0.1, 0])
        semicirc = Arc(fill_opacity=0,
                       angle=PI, 
                       stroke_width=5, 
                       color=GRAY_D).scale(0.35).move_to(np.add(
                           dot.get_center(), np.array([0, 0.1, 0])))
        line = Line(dot.get_center(), 
                    np.array([x + 0.3, y1 + 0.3, 0]),
                    stroke_width=5,
                    color=GRAY_D)
        square = Square(side_length = 1,
                        color=YELLOW_A,
                        fill_color=YELLOW_A,
                        fill_opacity=1).move_to([x, y1, 0])
        group = VGroup(square, dot, line, semicirc)

        line_measure_1 = Line(np.array([x-0.07, y1, 0]),
                              np.array([x-0.07, y2+0.4, 0]), 
                              stroke_width = 5, 
                              color = YELLOW_A)
        line_measure_2 = Line(np.array([x+0.07, y1, 0]), 
                              np.array([x+0.07, y2+0.4, 0]), 
                              stroke_width =5, 
                              color = YELLOW_A)
        measure_tip = Triangle(color = YELLOW_A, 
                               fill_color = YELLOW_A, 
                               fill_opacity
                               = 1).scale(0.3).rotate(60*DEGREES).move_to([x,
                                                                           y2+0.4, 0])
        gate = VGroup(line_measure_1, line_measure_2, measure_tip, group)
        return gate

    def barrier(self, x, y1, y2): 
        # aesthetic barrier 
        rect = Rectangle(width=0.5, 
                         height=abs(y2-y1)+1,
                         fill_color=GRAY_B,
                         fill_opacity=0.8,
                         stroke_width=0).move_to(
                                 [x,min(y1,y2)+abs(y1-y2)/2, 0])
        min_y, max_y = min(y1,y2), max(y1,y2)
        dotted_line = DashedLine(start=np.array([x, min_y-0.5, 0]), 
                                 end=np.array([x, max_y+0.5, 0]),
                                 color=GRAY_E,
                                 stroke_width=1.5)
        barrier = VGroup(rect, dotted_line)
        return barrier

    # controlled pauli gates
    # each has a different design 
    def cx(self, x1, y1, y2):
        # control qubit
        dot = Dot(point = np.array([x1, y1, 0]), 
                  radius = 0.15, 
                  color = BLUE_E)
        # target qubit 
        circle = Circle(radius = 0.5, 
                        color = BLUE_E, 
                        fill_opacity = 1).move_to([x1, y2, 0]) 
        plus = VGroup(
                Line(start = np.array([x1- 0.3, y2, 0]), 
                     end = np.array([x1+ 0.3, y2, 0]),
                     stroke_width = 2), 
                Line(start = np.array([x1, y2 - 0.3, 0]),
                     end = np.array([x1, y2 + 0.3, 0]),
                     stroke_width = 2))
        circle = VGroup(circle, plus)

        # line in between   
        if y2 < y1: 
            end = np.array([x1, y2 + 0.5, 0])
        else: 
            end = np.array([x1, y2 - 0.5, 0])

        line = Line(start = np.array([x1, y1, 0]), 
                    end = end, 
                    color = BLUE_E,
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
    
    def ctext(self, x1, y1, y2, params = None, param_location = None): 
        # control qubit 
        dot1 = Dot(point = np.array([x1, y1, 0]), 
                  radius = 0.15, 
                  color = BLUE_C) 
        # target qubit
        dot2 = Dot(point = np.array([x1, y2, 0]),
                  radius = 0.15, 
                  color = BLUE_C)
        # line in between 
        line = Line(start = np.array([x1, y1, 0]), 
                    end = np.array([x1, y2, 0]), 
                    color = BLUE_C)
        if params: 
            y_param = min(y1,y2) + 1
            if params[1]: 
                param_text = MathTex(rf"{params[0]} \; ({params[1][0]:.1f})",
                                     font_size = 40,
                                     fill_color = WHITE,
                                     fill_opacity=1).move_to(
                                             [x1+1, y_param, 0])
            else: 
                param_text = MathTex(rf"{params[0]}", 
                                     font_size= 40, 
                                     fill_color=WHITE, 
                                     fill_opacity=1).move_to(
                                             [x1+0.5, y_param, 0])
            gate = VGroup(dot1, dot2, line, param_text)
        else: 
            gate = VGroup(dot1, dot2, line)

        return gate 

    def swap(self, x1, y1, y2): 
        cross1 = Cross(stroke_color = BLUE_B, 
                       scale_factor = 0.25, stroke_width = 4).move_to([x1, y1, 0])
        cross2 = Cross(stroke_color = BLUE_B,
                       scale_factor = 0.25, stroke_width = 4).move_to([x1, y2, 0])

        line = Line(start = np.array([x1,y1,0]),
                    end = np.array([x1,y2,0]), 
                    color = BLUE_B)
        gate = VGroup(cross1, cross2, line)
        return gate

    # general controlled unitary gate
    def cgate(self, name, x1, y1, y2, y3 = None, color = MAROON_D, params = None): 
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
                               height=label.height).move_to(label.get_center())
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
                    height=math.ceil(group.height + 0.4), 
                    fill_color=color, color=color,
                    fill_opacity=1).move_to(group.get_center()),
                group).move_to([x1, np.mean([y1, y2]), 0])
        return gate

class BuildCircuit(Scene):
    # build a visual manim circuit from a qiskit QuantumCircuit() object
    def construct(self, run_time=0.5):

        qc = random_circuit(5, max_operands = 2, depth = 3)
        qc.measure_all()


        mobjects = self.build(qc)
        circuit = VGroup(*mobjects)

        wire_pos = list(range(-qc.num_qubits+1, qc.num_qubits, 2)) 
        cwires = VGroup()
        if qc.num_clbits != 0: 
            min_qwire = min(wire_pos)
            c_wire_pos = min(wire_pos) - 2
            cwires.add(Line(start=np.array(
                                [circuit.get_center()[0]-circuit.width/2-0.3, c_wire_pos+0.03, 0]), 
                            end=np.array(
                                [circuit.get_center()[0]+circuit.width/2+0.3, c_wire_pos+0.03, 0]), 
                            stroke_width=3, 
                            color=YELLOW_A))
            cwires.add(Line(start=np.array(
                                [circuit.get_center()[0]-circuit.width/2-0.3,
                                 c_wire_pos-0.06, 0]), 
                            end=np.array(
                                [circuit.get_center()[0]+circuit.width/2+0.3,
                                 c_wire_pos-0.06, 0]),
                            stroke_width=3, 
                            color=YELLOW_A))
            cwires.add(Line(start=np.array(
                                [circuit.get_center()[0]-circuit.width/2-0.05,
                                 c_wire_pos-0.1, 0]), 
                            end=np.array(
                                [circuit.get_center()[0]-circuit.width/2+0.05,
                                 c_wire_pos+0.1, 0]), 
                            stroke_width=5, 
                            color=YELLOW_A))
            cwires.add(MathTex(rf"C", 
                               font_size=55).move_to(
                                   [circuit.get_center()[0]-circuit.width/2-1, 
                                    c_wire_pos, 0]))
            cwires.add(MathTex(rf"{qc.num_clbits}", 
                               font_size=35).move_to(
                                   [circuit.get_center()[0]-circuit.width/2-0.15, 
                                    c_wire_pos+0.25, 0]))


        qwires = VGroup()
        idx = qc.num_qubits
        for wire in wire_pos: 
            qwires.add(Line(start=np.array([circuit.get_center()[0]-circuit.width/2-0.3, wire, 0]), 
                             end=np.array([circuit.get_center()[0]+circuit.width/2+0.3, wire, 0]), 
                             stroke_width=5))
            qwires.add(MathTex(rf"q_{idx-1}", 
                              font_size = 55).move_to(
                                  [circuit.get_center()[0]-circuit.width/2-1, wire, 0]))
            idx-=1
        
        circuit_full = VGroup(cwires, qwires, circuit).move_to([0, 0, 0])
        scaling_factor = min(config.frame_width/circuit_full.width,
                             config.frame_height/circuit_full.height)
        circuit_full.scale(scaling_factor)

        # Step 5: Animate the circuiti
        self.add(circuit_full)

    def decompose(self, qc):
        # provided a qiskit QuantumCircuit() object
        # extract the visual parameters for building 
        # in Manim
        with open('gates.json', 'r') as file:
            quantum_gates = json.load(file)

        def categorize_gate(gate_name):
            gate_name = gate_name.lower()
            for category, gates in quantum_gates.items():
                for gate in gates:
                    if gate_name == gate['name']:
                        if 'color' in gate:
                            return category, gate['latex'], gate['color']
                        else: 
                            return category, gate['latex'], 'MAROON_C'

        categories, names, params, colors, qbits, cbits = [], [], [], [], [], []
        for instruction in qc.data:
            category, latex, color = categorize_gate(instruction.operation.name)
            categories.append(category)
            names.append(latex)
            colors.append(color)
            params.append([i for i in instruction.operation.params if
                           isinstance(i, (float, np.floating))])

            qbits.append([qc.find_bit(qubit).index for qubit in instruction.qubits])
            cbits.append([qc.find_bit(clbit).index for clbit in instruction.clbits])

        circuit_data = pd.DataFrame({
            'category': categories,
            'names': names,
            'colors': colors,
            'params': params,
            'qbits': qbits,
            'cbits': cbits
        })

        return circuit_data


    def build_flat(self, qc, gap=0.8):
        # for two qubit circuits
        circuit_data = self.decompose(qc)
        q0x, q1x = 0, 0
        circuit = []

        # algorithm to place quantum gates on a circuit
        for idx, elements in circuit_data.iterrows():
            category, name = elements['category'], elements['names']
            params, qubits = elements['params'], elements['qbits']
            cbits = elements['cbits']
            
            x, y, q0, q1, reduce = 0, 0, False, False, False
            if len(qubits) > 1:  
                y1, y2 = (1, -1) if qubits == [0, 1] else (-1, 1)
                x = max(q0x, q1x)
                q0, q1 = True, True
            else:  
                if qubits == [0]:
                    x, y, q0 = q0x, 1, True
                elif qubits == [1]:
                    x, y, q1 = q1x, -1, True

            if category == 'single_qubit_gates':
                init = Gates().single(name, x=x, y=y, params=params)
                x += init.width/2
                if len(params) == 3: 
                    reduce = True
                gate = Gates().single(name, x=x, y=y, params=params)
            elif category == 'cx_like_gates':
                if name.lower() in ['cx', 'cnot']: 
                    init = Gates().cx(x, y1, y2)
                    x += init.width
                    gate = Gates().cx(x, y1, y2)
                elif name.lower() == 'cy': 
                    init = Gates().cy(x, y1, y2)
                    x += init.width/2
                    gate = Gates().cy(x, y1, y2)
                elif name.lower() == 'cz': 
                    init = Gates().ctext(x, y1, y2)
                    x += init.width/2
                    gate = Gates().ctext(x, y1, y2)
                elif name.lower() == 'swap': 
                    init = Gates().swap(x, y1, y2)
                    x += init.width/2
                    gate = Gates().swap(x, y1, y2)
            elif category == 'cphase_gates':
                init = Gates().ctext(x, y1, y2, params=[name, params])
                x += init.width/2
                gate = Gates().ctext(x, y1, y2, params=[name, params])
            elif category == 'general_controlled_gates':
                init = Gates().cgate(name, x, y1, y2, params=params)
                x += init.width/2
                gate = Gates().cgate(name, x, y1, y2, params=params)
            elif category == 'multi_qubit_gates':
                init = Gates().multi(name, x, y1, y2, params=params, idxs=qubits)
                x += init.width/2
                gate = Gates().multi(name, x, y1, y2, params=params, idxs=qubits)

            circuit.append(gate)
            if q0 and q1: 
                max_gate_width = gate.width + gap 
                q0x = q1x = max(q0x + max_gate_width, q1x + max_gate_width)
            elif q0: 
                q0x += gate.width + gap
                if reduce: q0x -= gap/2
            elif q1: 
                q1x += gate.width + gap 
                if reduce: q1x -= gap/2

        return circuit

    def build(self, qc, gap = 1): 
        circuit_data = self.decompose(qc) 
        num_qubits = qc.num_qubits
        wire_y_pos = np.array(range(num_qubits-1, -num_qubits, -2))
        
        circuit, x = [], np.zeros(num_qubits)
        for idx, elements in circuit_data.iterrows():
            category, name = elements['category'], elements['names']
            params, qubits = elements['params'], elements['qbits']
            cbits = elements['cbits']
            color = elements['colors']

            y_gate = wire_y_pos[qubits].tolist()

            if category == 'single_qubit_gates': 
                x_gate = x[qubits].tolist()[0]
                y_gate = y_gate[0]
                init = Gates().single(name, x=x_gate, y=y_gate, params=params)
                if x[qubits] != 0: 
                    x_gate += init.width/2
                    x[qubits] += init.width/2
                gate = Gates().single(name, x=x_gate, y=y_gate, color=color, params=params)
                x[qubits] += gate.width/2 + gap
                circuit.append(gate)
                continue 

            else: 
                min_idx, max_idx = min(qubits), max(qubits)
                between = x[min_idx:max_idx+1] 
                x[min_idx:max_idx+1] = np.ones(len(between)) * max(between)
                x_gate = max(x[qubits].tolist())
                x_coords, zeros = x[qubits], np.zeros(len(qubits))

            if category == 'cx_like_gates': 
                if name.lower() in ['cx', 'cnot']: 
                    init = Gates().cx(0, 0, 0)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().cx(x_gate, y_gate[0], y_gate[1]) 
                if name.lower() == 'cy': 
                    init = Gates().cx(0, 0, 0)
                    if not np.allclose(x_coords, zeros):
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().cy(x_gate, y_gate[0], y_gate[1])
                if name.lower() == 'cz':
                    init = Gates().ctext(0, 0, 0)
                    if not np.allclose(x_coords, zeros):
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().ctext(x_gate, y_gate[0], y_gate[1])
                if name.lower() == 'swap': 
                    init = Gates().swap(0, 0, 0)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2   
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().swap(x_gate, y_gate[0], y_gate[1])
                if name.lower() == 'measure': 
                    init = Gates().measure(0, 0, 0)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[:] += init.width + gap 
                    gate = Gates().measure(x_gate, y_gate[0], min(wire_y_pos)-2.08)
                if name.lower() == 'barrier': 
                    init = Gates().barrier(0, 0, 1)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width + gap
                    gate = Gates().barrier(x_gate, min(y_gate), max(y_gate))

            elif category == 'cphase_gates': 
                init = Gates().ctext(0, 0, 0, params=[name, params])
                param_location = False
                if abs(qubits[0]-qubits[1]) % 2 == 0: 
                    param_location = True
                if not np.allclose(x_coords, zeros): 
                    x_gate += init.width/2
                    x[min_idx:max_idx+1] += init.width/2
                gate = Gates().ctext(x_gate, y_gate[0], y_gate[1], 
                                     params=[name, params], 
                                     param_location = param_location)

            elif category == 'general_controlled_gates':
                init = Gates().cgate(name, 0, 0, 0, params=params)
                if not np.allclose(x_coords, zeros): 
                    x_gate += init.width/2
                    x[min_idx:max_idx+1] += init.width/2
                gate = Gates().cgate(name, x_gate, y_gate[0], y_gate[1],
                                     params=params)

            elif category == 'multi_qubit_gates': 
                init = Gates().multi(name, 0, 0, 0, params=params, idxs=qubits)
                if not np.allclose(x_coords, zeros): 
                    x_gate += init.width/2
                    x[min_idx:max_idx+1] += init.width/2
                gate = Gates().multi(name, x_gate, y_gate[0], y_gate[1], 
                                     params=params, idxs=qubits)

            x[min_idx:max_idx+1] += gate.width/2 + gap
            circuit.append(gate)

        return circuit














            




if __name__ == "__main__":
    qc = random_circuit(5, depth = 1, max_operands = 2)
    qc.rzz(0.4, 0, 3)
    qc.rxx(0.4, 4, 0)
    print(qc)

    #config.pixel_height = 480  # Set pixel height for low resolution
    #config.pixel_width = 854    # Set pixel width for low resolution

    build_circuit_scene = BuildCircuit() 
    build_circuit_scene.construct(qc)







