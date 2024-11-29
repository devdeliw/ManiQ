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
        ctext = self.ccz(0, 3, -3, 0)
        self.add(ctext)

    def single(self, name, x, y, color=MAROON_D, params=None):
        # -- default single qubit gates
        label = MathTex(rf"{name}", font_size=55)
        if params:
            param_str = ", ".join([f"{param:.2f}" for param in params])
            label2 = MathTex(rf"{param_str}", font_size=30).next_to(label, DOWN * 0.1)
            label.shift(UP * 0.1)
            label_group = VGroup(label, label2)
        else:
            label_group = VGroup(label)

        border = Rectangle(
            width=max(1, label_group.width + 0.4), 
            height=1,
            fill_color=color, 
            fill_opacity=1,
            color=color
        ).move_to([x, y, 0])

        label_group.move_to(border.get_center())
        gate = VGroup(border, label_group).move_to([x, y, 0])
        return gate

    def measure(self, x, y1, y2):
        # -- measurement gate 
        ## -- measurement qubit
        dot = Dot(radius=0.05, color=GRAY_D).move_to([x, y1 - 0.1, 0])
        semicirc = Arc(
            fill_opacity=0, angle=PI, stroke_width=2, color=GRAY_D
        ).scale(0.35).move_to(dot.get_center() + np.array([0, 0.1, 0]))
        line = Line(
            dot.get_center(), np.array([x + 0.3, y1 + 0.3, 0]),
            stroke_width=2, color=GRAY_D
        )
        square = Square(
            side_length=1, color=YELLOW_A, fill_color=YELLOW_A,
            fill_opacity=1
        ).move_to([x, y1, 0])
        group = VGroup(square, dot, line, semicirc)

        ## -- measurement lines to classical register
        line_measure_1 = Line(
            np.array([x - 0.07, y1, 0]), np.array([x - 0.07, y2 + 0.4, 0]),
            stroke_width=2, color=YELLOW_A
        )
        line_measure_2 = Line(
            np.array([x + 0.07, y1, 0]), np.array([x + 0.07, y2 + 0.4, 0]),
            stroke_width=2, color=YELLOW_A
        )
        measure_tip = Triangle(
            color=YELLOW_A, fill_color=YELLOW_A, fill_opacity=1
        ).scale(0.3).rotate(60 * DEGREES).move_to([x, y2 + 0.4, 0])

        gate = VGroup(line_measure_1, line_measure_2, measure_tip, group)

        return gate

    def barrier(self, x, y1, y2):
        # -- simple aesthetic barrier 
        rect = Rectangle(
            width=0.5, 
            height=np.abs(y2 - y1) + 1,
            fill_color=GRAY_B, 
            fill_opacity=0.8, 
            stroke_width=0
        ).move_to([x, np.min(y1, y2) + np.abs(y1 - y2) / 2, 0])

        dotted_line = DashedLine(
            start=np.array([x, min(y1, y2) - 0.5, 0]),
            end=np.array([x, max(y1, y2) + 0.5, 0]),
            color=GRAY_E, stroke_width=1.5
        )

        barrier = VGroup(rect, dotted_line)

        return barrier

    # --  controlled pauli gates
    def cx(self, x1, y1, y2):
        # -- CNOT gate 

        ## --  control qubit
        dot = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=BLUE_E)

        ## -- target qubit
        circle = Circle(
            radius=0.5, color=BLUE_E, fill_opacity=1
        ).move_to([x1, y2, 0])
        plus = VGroup(
            Line(
                start=np.array([x1 - 0.3, y2, 0]), 
                end=np.array([x1 + 0.3, y2, 0]),
                stroke_width=2
            ),
            Line(
                start=np.array([x1, y2 - 0.3, 0]), 
                end=np.array([x1, y2 + 0.3, 0]),
                stroke_width=2
            )
        )
        circle = VGroup(circle, plus)

        ## -- line connecting control & target qubits  
        line = Line(
            start=np.array([x1, min(y1, y2), 0]), end=np.array([x1, max(y1, y2), 0]),
            color=BLUE_E, stroke_width=5
        )

        gate = VGroup(line, dot, circle)

        return gate

    def cy(self, x1, y1, y2):
        # -- CY gate

        ## -- control qubit  
        dot = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=MAROON_C)

        ## -- target qubit
        target = self.single("Y", x1, y2, color=MAROON_C)

        ## -- line connecting control & target qubits 
        line = Line(
            start=np.array([x1, min(y1, y2), 0]), end=np.array([x1, max(y1, y2), 0]),
            color=MAROON_C, stroke_width=5
        )

        gate = VGroup(line, dot, target)

        return gate

    def ctext(self, x1, y1, y2, params=None):
        # -- arbitrary controlled-gate without labels 
        # -- e.g. CZ gate 

        ## -- control qubit
        dot1 = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=BLUE_C)

        ## -- target qubit
        dot2 = Dot(point=np.array([x1, y2, 0]), radius=0.3, color=BLUE_C)

        ## -- line in between
        line = Line(
            start=np.array([x1, y1, 0]), end=np.array([x1, y2, 0]), color=BLUE_C
        )

        ## -- adding labels to right of quantum gate 
        ## -- and any additional parameters  
        if params:
            y_param = min(y1, y2) + 1
            if params[1]:
                param_text = MathTex(
                    rf"{params[0]} \; ({params[1][0]:.1f})",
                    font_size=40, fill_color=WHITE, fill_opacity=1
                ).move_to([x1 + 1, y_param, 0])
            else:
                param_text = MathTex(
                    rf"{params[0]}",
                    font_size=40, fill_color=WHITE, fill_opacity=1
                ).move_to([x1 + 0.5, y_param, 0])
            gate = VGroup(dot1, dot2, line, param_text)
        else:
            gate = VGroup(dot1, dot2, line)

        return gate

    def swap(self, x1, y1, y2):
        # SWAP gate 
        cross1 = Cross(
            stroke_color=BLUE_E, scale_factor=0.4, stroke_width=4
        ).move_to([x1, y1, 0])
        cross2 = Cross(
            stroke_color=BLUE_E, scale_factor=0.4, stroke_width=4
        ).move_to([x1, y2, 0])
        line = Line(
            start=np.array([x1, y1, 0]), end=np.array([x1, y2, 0]),
            color=BLUE_E, stroke_width=5
        )

        gate = VGroup(cross1, cross2, line)

        return gate

    def cgate(self, name, x1, y1, y2, color=MAROON_C, params=None):
        # -- general controlled unitary gate 

        ## --  control qubit
        dot = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=color)

        ## -- target qubit
        target = self.single(name, x1, y2, color=color, params=params)

        # line in between control & target qubit
        end = np.array([x1, y2 + 0.5, 0]) if y2 < y1 else np.array([x1, y2 - 0.5, 0])
        line = Line(
            start=np.array([x1, y1, 0]), end=end, stroke_width=5, color=color
        )

        gate = VGroup(dot, target, line)

        return gate

    def fredkin(self, x1, y1, y2, y3):
        # -- CSWAP gate 

        ## -- controlled qubit 
        dot = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=BLUE_E)

        ## -- target qubits 
        cross1 = Cross(
            stroke_color=BLUE_E, scale_factor=0.4, stroke_width=4
        ).move_to([x1, y2, 0])
        cross2 = Cross(
            stroke_color=BLUE_E, scale_factor=0.4, stroke_width=4
        ).move_to([x1, y3, 0])

        ## -- line connecting all three qubits
        line = Line(
            start=np.array([x1, min(y1, y2, y3), 0]),
            end=np.array([x1, max(y1, y2, y3), 0]), color=BLUE_E
        )

        gate = VGroup(dot, cross1, cross2, line)

        return gate

    def ccx(self, x1, y1, y2, y3):
        # -- CCX gate 

        ## -- control qubits 
        dot1 = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=BLUE_E)
        dot2 = Dot(point=np.array([x1, y2, 0]), radius=0.3, color=BLUE_E)

        ## -- target qubit
        circle = Circle(
            radius=0.5, color=BLUE_E, fill_opacity=1
        ).move_to([x1, y3, 0])
        plus = VGroup(
            Line(
                start=np.array([x1 - 0.3, y3, 0]), end=np.array([x1 + 0.3, y3, 0]),
                stroke_width=2
            ),
            Line(
                start=np.array([x1, y3 - 0.3, 0]), end=np.array([x1, y3 + 0.3, 0]),
                stroke_width=2
            )
        )
        circle = VGroup(circle, plus)

        ## -- line connecting all three qubits 
        line = Line(
            start=np.array([x1, min(y1, y2, y3), 0]),
            end=np.array([x1, max(y1, y2, y3), 0]), color=BLUE_E, stroke_width=5
        )

        gate = VGroup(line, dot1, dot2, circle)

        return gate

    def ccz(self, x1, y1, y2, y3):
        # -- CCZ gate 

        dot1 = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=BLUE_C)
        dot2 = Dot(point=np.array([x1, y2, 0]), radius=0.3, color=BLUE_C)
        dot3 = Dot(point=np.array([x1, y3, 0]), radius=0.3, color=BLUE_C)

        ## -- line connecting all three 
        line = Line(
            start=np.array([x1, min(y1, y2, y3), 0]),
            end=np.array([x1, max(y1, y2, y3), 0]), color=BLUE_C, stroke_width=5
        )
        gate = VGroup(line, dot1, dot2, dot3)
        return gate

    def ccgate(self, name, x1, y1, y2, y3, params=None):
        # -- abitary two-control-qubit unitary gates 

        ## -- control qubits 
        dot1 = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=MAROON_C)
        dot2 = Dot(point=np.array([x1, y2, 0]), radius=0.3, color=MAROON_C)

        ## -- target qubit 
        target = self.single(name, x1, y3, params=params, color=MAROON_C)

        ## -- line connecting all three qubits
        line = Line(
            start=np.array([x1, min(y1, y2, y3), 0]),
            end=np.array([x1, max(y1, y2, y3), 0]), stroke_width=5, color=MAROON_C
        )

        gate = VGroup(line, dot1, dot2, target)

        return gate

    def cccgate(self, name, x1, y1, y2, y3, y4, params=None):
        # -- arbitrary three-control-qubit gates 

        ## -- control qubits
        dot1 = Dot(point=np.array([x1, y1, 0]), radius=0.3, color=MAROON_C)
        dot2 = Dot(point=np.array([x1, y2, 0]), radius=0.3, color=MAROON_C)
        dot3 = Dot(point=np.array([x1, y3, 0]), radius=0.3, color=MAROON_C)

        ## -- target qubits 
        target = self.single(name, x1, y4, params=params, color=MAROON_C)

        ## -- line connecting all qubits
        line = Line(
            start=np.array([x1, min(y1, y2, y3, y4), 0]),
            end=np.array([x1, max(y1, y2, y3, y4), 0]), stroke_width=5,
            color=MAROON_D
        )

        gate = VGroup(line, dot1, dot2, dot3, target)

        return gate

    def multiqubit(self, name, x, y, color=MAROON_D, params=None, idxs=None):
        # -- create label for the gate
        label = MathTex(rf"{name}", font_size=60).move_to([x + 0.5, np.mean(y), 0])
        group = VGroup(label)

        # -- add parameter text if provided
        if params:
            param_str = MathTex(", ".join(f"{param:.2f}" for param in params), font_size=40).next_to(label, DOWN)
            group.add(param_str)

        # -- create backbone rectangle of the gate
        group_rect = Rectangle(
            width=label.width + 0.1, height=label.height
        ).move_to(label.get_center())

        # -- add qubit labels to match ibm qiskit's aesthetic
        idxs_ = VGroup()
        y_ = y.copy()
        if idxs:
            for i, idx_value in enumerate(idxs):
                idx = MathTex(rf"{idx_value}", font_size=60).move_to([x - 0.3, max(y_), 0])
                idxs_.add(idx)
                y_.remove(max(y_))
            idxs_.next_to(group_rect, LEFT)

        # -- combine group with qubit labels
        group.add(idxs_)

        # -- create and position the gate
        gate = VGroup(
            Rectangle(
                width=group.width + 0.3,
                height=math.ceil(group.height + 0.4),
                fill_color=color,
                color=color,
                fill_opacity=1
            ).move_to(group.get_center()),
            group
        ).move_to([x, np.mean(y), 0])

        return gate


class BuildCircuit(Scene):
    # build a visual manim circuit from a qiskit QuantumCircuit() object
    def construct(self, qc, run_time=3):

        def reorder_instructions(qc):
            qubit_times = {i: 0 for i in range(qc.num_qubits)}
            ordered_instructions = []

            for instruction in qc.data:
                qubits = [qc.find_bit(qubit).index for qubit in instruction.qubits]
                start_time = max(qubit_times[q] for q in qubits)
                ordered_instructions.append((start_time, instruction))
                
                min_qubit, max_qubit = min(qubits), max(qubits)
                for q in range(min_qubit, max_qubit+1):
                    qubit_times[q] = start_time + 1

            ordered_instructions.sort(key=lambda x: x[0])

            new_qc = QuantumCircuit(qc.num_qubits)
            new_qc.add_register(*qc.cregs)
            for _, inst in ordered_instructions:
                new_qc.append(inst.operation, inst.qubits, inst.clbits)
            
            return new_qc

        qc = reorder_instructions(qc)
        mobjects = self.build(qc)
        wire_pos = list(range(-qc.num_qubits+1, qc.num_qubits, 2))
        
        def group_by_column(objects):
            gate_count = 0
            columns = []
            processed = set()
            while gate_count < len(objects):
                start_object = objects[gate_count]
                start_height = start_object.height
                start_y = start_object.get_y()

                initial_wires = [
                    wire for wire in wire_pos
                    if start_y-start_height/2 <= wire <= start_y+start_height/2
                ]

                filtered_objects = []
                for obj in objects[gate_count+1:]:
                    intersecting_wires = [
                        wire for wire in wire_pos
                        if obj.get_y()-obj.height/2 <= wire <= obj.get_y()+obj.height/2
                    ]
                    if all(obj not in col for col in columns):
                        if abs(obj.get_x() - start_object.get_x()) <= 2:
                            if not any(val in initial_wires for val in intersecting_wires):
                                if obj not in filtered_objects: 
                                    filtered_objects.append(obj)

                individual_column = [start_object]
                intersecting_wires = [
                    num for num in wire_pos if start_y-start_height/2 <= num <= start_y+start_height/2
                ]

                stored_y_positions = set(intersecting_wires)
                for obj in filtered_objects:
                    obj_y = obj.get_y()
                    obj_height = obj.height

                    current_intersecting_wires = [
                        num for num in wire_pos if obj_y-obj_height <= num <= obj_y+obj_height
                    ]
                    if not any(y_pos in stored_y_positions for y_pos in current_intersecting_wires):
                        individual_column.append(obj)
                        stored_y_positions.update(current_intersecting_wires)
                        gate_count+=1

                columns.append(individual_column)
                gate_count+=1

            return columns
        

        def align_by_column(columns, pad = 0.08):
            final_mobjects = []
            start = 0
            for col in columns:
                midpoint = max(mobject.get_x() for mobject in col) + start
                for mobject in col:
                    final_mobjects.append(mobject.move_to([midpoint+pad, mobject.get_y(), 0]))
                start+=pad

            return final_mobjects


        final_mobjects = align_by_column(group_by_column(mobjects))
        circuit = VGroup(*final_mobjects)

        cwires = VGroup()
        if qc.num_clbits != 0: 
            min_qwire = min(wire_pos)
            c_wire_pos = min(wire_pos) - 2
            cwires.add(Line(start=np.array(
                                [circuit.get_center()[0]-circuit.width/2-0.3, c_wire_pos+0.03, 0]), 
                            end=np.array(
                                [circuit.get_center()[0]+circuit.width/2+0.3, c_wire_pos+0.03, 0]), 
                            stroke_width=2, 
                            color=YELLOW_A))
            cwires.add(Line(start=np.array(
                                [circuit.get_center()[0]-circuit.width/2-0.3,
                                 c_wire_pos-0.06, 0]), 
                            end=np.array(
                                [circuit.get_center()[0]+circuit.width/2+0.3,
                                 c_wire_pos-0.06, 0]),
                            stroke_width=2, 
                            color=YELLOW_A))
            cwires.add(Line(start=np.array(
                                [circuit.get_center()[0]-circuit.width/2-0.05,
                                 c_wire_pos-0.2, 0]), 
                            end=np.array(
                                [circuit.get_center()[0]-circuit.width/2+0.05,
                                 c_wire_pos+0., 0]), 
                            stroke_width=2, 
                            color=YELLOW_A))
            cwires.add(Text("meas", 
                           font_size=55).move_to(
                           [circuit.get_center()[0]-circuit.width/2-1.5, 
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
 
        self.play(Write(circuit_full), run_time = run_time)
        #self.wait()

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
                if not np.allclose(x_coords, zeros): 
                    x_gate += init.width/2
                    x[min_idx:max_idx+1] += init.width/2
                gate = Gates().ctext(x_gate, y_gate[0], y_gate[1], 
                                     params=[name, params])

            elif category == 'general_controlled_gates':
                init = Gates().cgate(name, 0, 0, 0, params=params)
                if not np.allclose(x_coords, zeros): 
                    x_gate += init.width/2
                    x[min_idx:max_idx+1] += init.width/2
                gate = Gates().cgate(name, x_gate, y_gate[0], y_gate[1],
                                     params=params)

            elif category == 'multi_qubit_gates': 
                init = Gates().multiqubit(name, 0, [0]*len(qubits), params=params, idxs=qubits)

                sorted_idxs = sorted(range(len(qubits)), key=lambda x: qubits[x])

                if not np.allclose(x_coords, zeros): 
                    x_gate += init.width/2
                    x[min_idx:max_idx+1] += init.width/2
                gate = Gates().multiqubit(name, x_gate, y_gate,
                                          color=color, params=params,
                                          idxs=sorted_idxs)

            elif category == 'multi_controlled_gates': 

                if name.lower() == 'ccx': 
                    init = Gates().ccx(0, 0, 0, 0)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().ccx(x_gate, y_gate[0], y_gate[1], y_gate[2])

                elif name.lower() == 'ccy': 
                    init = Gates().ccy(0, 0, 0, 0)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2 
                    gate = Gates().ccy(x_gate, y_gate[0], y_gate[1], y_gate[2])

                elif name.lower() == 'ccz':
                    init = Gates().ccx(0, 0, 0, 0)
                    if not np.allclose(x_coords, zeros):
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().ccz(x_gate, y_gate[0], y_gate[1], y_gate[2])

                elif name.lower() == 'cswap': 
                    init = Gates().fredkin(0, 0, 0, 0)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] ++ init.width/2
                    gate = Gates().fredkin(x_gate, 
                                           y_gate[0], y_gate[1], y_gate[2])

                else: 
                    init = Gates().cccgate(name, 
                                           0, 0, 0, 0, 0, 
                                           params=params)
                    if not np.allclose(x_coords, zeros): 
                        x_gate += init.width/2
                        x[min_idx:max_idx+1] += init.width/2
                    gate = Gates().cccgate(name, x_gate, 
                                         y_gate[0], y_gate[1],
                                         y_gate[2], y_gate[3], params=params)

            x[min_idx:max_idx+1] += gate.width/2 + gap
            circuit.append(gate)

        return circuit














            




if __name__ == "__main__":
    qc = random_circuit(3, depth = 10)
    print(qc)
    build_circuit_scene = BuildCircuit() 
    build_circuit_scene.construct(qc)







