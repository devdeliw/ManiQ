from manim import * 
from manim.opengl import *
from random_circuit import random_circuit
from qiskit import QuantumCircuit

from gates import Gates
from updaters import global_cursor_to_manim
from qiskit_functions.convert_to_manim import ConvertToManim

import ruamel.yaml as yaml 
import numpy as np 
import pandas as pd 

config.preview = True
config.write_to_movie = False 
config.renderer = 'opengl'
config.fullscreen = False

pd.set_option("display.expand_frame_repr", True)
pd.set_option("display.max_columns", 8)


class ManiQCircuit(Scene, Gates): 
    """ 
    Class to convert Qiskit QuantumCircuit object into 
    ManiQCircuit mobject for display. 

    """

    def sort_instructions(self):

        qc = QuantumCircuit(2)
        qc.h([0, 1])
        qc.cz(0,1)
        qc.ry(np.pi/3 , 0)
        qc.rx(np.pi/5, 1)
        qc.measure_all()
        self.qc = qc
        



        """ 
        Logic to sort qiskit circuit to ensure no manim gate overlap. 

        Returns: 
            The sorted instruction array as self attribute.
        """
        
        # Sorting instructions based on their avilable start time
        qubit_times = {i: 0 for i in range(self.qc.num_qubits)}

        # Initialize list to store sorted QuantumCircuit instructions 
        sorted_instructions = [] 

        for instruction in self.qc.data: 
            # Qubit idxs being acted on by instruction 
            instruction_qubits = [self.qc.find_bit(qubit).index for qubit in instruction.qubits]
            min_qubit, max_qubit = min(instruction_qubits), max(instruction_qubits) 

            # Define instruction start time as maximum available start time 
            # across all instruction qubits
            start_time = max(qubit_times[q] for q in range(min_qubit, max_qubit+1))
            sorted_instructions.append((start_time, instruction)) 

            # Increases possible start time for all instruction qubits by 1
            if instruction.operation.name == 'measure': 
                for q in range(0, self.qc.num_qubits+1): 
                    qubit_times[q] = start_time + 1
            else: 
                for q in range(min_qubit, max_qubit+1): 
                    qubit_times[q] = start_time + 1

        sorted_instructions.sort(key=lambda q: q[0])

        self.sorted_instructions = sorted_instructions 
        return 

    def decompose(self): 
        """
        Decomposes qiskit QuantumCircuit into sorted DataFrame object 
        containing general information for each QuantumCircuit gate. 

        Returns: 
            DataFrame object as self attribute. 

        """

        # Load yaml file containing gate information
        try: 
            with open('gates.yaml', 'r') as f: 
                gate_params = yaml.safe_load(f) 
        except FileNotFoundError:
            raise FileNotFoundError("The 'gates.yaml' file was not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing 'gates.yaml': {e}")

        # Initialize list to store all instruction information 
        data_records = [] 

        for start_time, instruction in self.sorted_instructions: 
            operation_name = instruction.operation.name 
            instruction_params = gate_params.get(operation_name, {})

            # Extract gate parameters 
            category = instruction_params.get('category')
            latex = instruction_params.get('latex', operation_name) 
            color = instruction_params.get('color', 'MAROON_C') 

            params = [
                param for param in instruction.operation.params 
                if isinstance(param, (float, np.floating)) 
            ]

            # Qubit and Clbit indxs instruction acts on 
            qbits = [self.qc.find_bit(qubit).index for qubit in instruction.qubits] 
            cbits = [self.qc.find_bit(clbit).index for clbit in instruction.clbits] 

            data_records.append({
                'categories': category, 
                'start_times': start_time, 
                'names': latex, 
                'qiskit_names': operation_name,
                'colors': color, 
                'params': params, 
                'qbits': qbits, 
                'cbits': cbits, 
            })

        # Generate DataFrame
        self.circuit_data = pd.DataFrame(data_records) 

        # Sort based on start_time for better organization 
        self.circuit_data.sort_values(by='start_times', inplace=True)
        self.circuit_data.reset_index(drop=True, inplace=True)
        return

    def build_circuit(self, gap=0.5): 
        """
        Builds the ManiQ circuit before rendering takes place. 
        Currently does not include qubit wires because manim 
        has some z_index issues currently. 

        Args: 
            gap (float): Manim-space horizontal gap between columns of gates. 
        
        Returns: 
            The Manim circuit mobject. 

        """

        circuit_data = self.circuit_data 
        num_qubits = self.qc.num_qubits 
        num_clbits = self.qc.num_clbits 

        # y coordinates for qubit and clbit wires 
        wire_y_pos = np.arange(num_qubits-1, -num_qubits, -2)
        # Only one classical register currently 
        clwire_y_pos = min(wire_y_pos)-3 


        # Will attach every gate with a unique ID 
        # Allowing user to remove individual gates
        gate_references = {}
        # List to store gates of same column in subarrays
        grouped_ids = []
        grouped_gates = [] 

        for time in range(max(circuit_data['start_times'])+1): 
            filtered_df = circuit_data[circuit_data['start_times'] == time] 

            # Gates with identical start times are grouped in same column 
            column_group = []
            column_ids = []
            for _, elements in filtered_df.iterrows(): 
                category = elements['categories'] 
                name = elements['names'] 
                qiskit_name = elements['qiskit_names']
                color = elements['colors'] 
                params = elements['params'] 
                qbits = elements['qbits'] 

                y_value = wire_y_pos[qbits]

                # Building circuit, initially placing all circuit gates 
                # at x=0 position. Shifting appropriately afterwards

                if category == 'single_qubit_gate': 
                    gate = self.single(
                            name, 
                            x=0, 
                            y=y_value[0], 
                            color=color, 
                            params=params, 
                    ) 
                elif category == 'cx_like_gate': 
                    if hasattr(self, name.lower()):
                        method = getattr(self, name.lower())
                        if callable(method): 
                            if name.lower() != 'barrier': 
                                try: 
                                    gate = method(
                                            x=0, 
                                            y1=y_value[0], 
                                            y2=y_value[1], 
                                    )
                                except TypeError as e: 
                                    print(f"Error calling method {name.lower()} -- {e}")
                            else: 
                                try:
                                    gate = method( 
                                            x=0, 
                                            y1=min(y_value), 
                                            y2=max(y_value), 
                                    )
                                except TypeError as e: 
                                    print(f"Error calling barrier method -- {e}")
                elif category == 'cphase_gate': 
                    gate = self.ctext(
                            x=0, 
                            y1=y_value[0], 
                            y2=y_value[1], 
                            params=[name, params], 
                    )
                elif category == 'general_controlled_gate': 
                    gate = self.cgate(
                            name=name,
                            x=0, 
                            y1=y_value[0], 
                            y2=y_value[1], 
                            params=params, 
                    )
                elif category == 'multi_qubit_gate': 
                    # Logic to sort idx labels properly 
                    sorted_idxs = sorted(range(len(qbits)), key=lambda x: qbits[x]) 
                    gate = self.multiqubit(
                            name=name, 
                            x=0, 
                            y=y_value, 
                            color=color, 
                            params=params,
                            idxs=sorted_idxs, 
                    )
                elif category == 'multi_controlled_gate': 
                    if name.lower() in ['ccx', 'ccy', 'ccz', 'cswap']: 
                        if hasattr(self, name.lower()): 
                            method = getattr(self, name.lower())
                            if callable(method): 
                                try: 
                                    gate = method(
                                            x=0, 
                                            y1=y_value[0], 
                                            y2=y_value[1], 
                                            y3=y_value[2], 
                                    )
                                except TypeError as e: 
                                    print(f"Error calling method {name.lower()} -- {e}") 
                    else: 
                        gate = self.cccgate(
                                name=name, 
                                x=0, 
                                y1=y_value[0], 
                                y2=y_value[1], 
                                y3=y_value[2], 
                                y4=y_value[3], 
                                params=params,
                        )
                elif category == 'measure': 
                    gate = self.measure(
                            x=0, 
                            y1=y_value[0], 
                            y2=clwire_y_pos, 
                    )
                else: 
                    raise UnboundLocalError(f'Unable to find gate category; gate {name} unbound.')

                # Unique identification to individual gate
                qubit_idxs = ''.join(map(str, qbits))
                gate_id = f'{qiskit_name}_{qubit_idxs}_{time}' 
                # Gate_id refers to mobject and its bounding box
                gate_references[gate_id] = gate 

                # Append gate to column 
                column_group.append(gate)
                column_ids.append(gate_id)

            # Adds entire column of gates as sublist 
            grouped_gates.append(column_group) 
            grouped_ids.append(column_ids)

        # Aligns all circuits in column and adds them to universal gate list
        start_pos = 0 
        gates = []
        gate_ids = []

        for col_idx in range(len(grouped_gates)): 
            column_gates = grouped_gates[col_idx]
            column_ids = grouped_ids[col_idx]
            # Aligns columns based on maximum column gate width 
            max_gate_width = max([gate.width for gate in column_gates])
            for gate_idx in range(len(column_gates)): 
                gate = column_gates[gate_idx]
                gate_id = column_ids[gate_idx]

                gate = gate.shift(RIGHT*(start_pos+max_gate_width/2))

                gates.append(gate)
                gate_ids.append(gate_id)

            start_pos += max_gate_width + gap
            
        # Universal gate mobject
        circuit = VGroup(*gates) 

        # Generating qubit and clbit wires 
        qwires = [] 
        idx = 0 
        for wire in wire_y_pos: 
            qwires.append(
                Line(
                    start=np.array([circuit.get_center()[0]-circuit.width/2-0.3, wire, 0]),
                    end=np.array([circuit.get_center()[0]+circuit.width/2+0.3, wire, 0]), 
                    stroke_width=5,
                )
            )
            qwires.append(
                MathTex(
                    rf"q_{idx}", 
                    fontsize=55, 
                ).move_to([circuit.get_center()[0]-circuit.width/2-1, wire, 0])
            )
            idx += 1
        qwires = VGroup(*qwires)

        cwires = [] 
        if num_clbits != 0: 
            cwires.append(
                Line(
                    start=np.array([circuit.get_center()[0]-circuit.width/2-0.3, clwire_y_pos+0.1, 0]), 
                    end=np.array([circuit.get_center()[0]+circuit.width/2+0.3, clwire_y_pos+0.1, 0]), 
                    stroke_width=2, 
                    color=YELLOW_A,
                    )
            )
            cwires.append(
                Line(
                    start=np.array([circuit.get_center()[0]-circuit.width/2-0.3, clwire_y_pos-0.1, 0]), 
                    end=np.array([circuit.get_center()[0]+circuit.width/2+0.3, clwire_y_pos-0.1, 0]),
                    stroke_widith=2, 
                    color=YELLOW_A
                )
            )
            cwires.append(
                Line(
                    start=np.array([circuit.get_center()[0]-circuit.width/2-0.05, clwire_y_pos-0.2, 0]), 
                    end=np.array([circuit.get_center()[0]-circuit.width/2+0.05, clwire_y_pos, 0]), 
                    stroke_width=2, 
                    color=YELLOW_A
                )
            )
            cwires.append(
                Text(
                    "meas", 
                    font_size=55
                ).move_to([circuit.get_center()[0]-circuit.width/2-1.5, clwire_y_pos, 0]))
            cwires.append(
                MathTex(
                    rf"{num_clbits}", 
                    font_size=35
                ).move_to([circuit.get_center()[0]-circuit.width/2-0.15, clwire_y_pos+0.3, 0]))
            idx += 1 
        cwires = VGroup(*cwires) 

        # Final circuit mobject 
        self.gate_ids = gate_ids
        self.gate_references = gate_references
        self.circuit = VGroup(circuit).move_to([0, 0, 0])
        return

    def assemble(self):
        """ 
        Performs Manim circuit assembly instructions in correct order. 

        """

        self.sort_instructions()
        self.decompose() 
        self.build_circuit() 

        # Default scaling of main circuit relative to pyglet window
        self.scaling_factor = min(
                config.frame_width/self.circuit.width, 
                config.frame_height/self.circuit.height, 
        )*0.8

        self.circuit.scale(self.scaling_factor)
        
        print(self.qc)
        print(self.circuit_data)
        return 

    def construct(self): 
        """
        Rendering Method. 

        """ 

        def show_circuit(): 
            self.play(self.camera.animate.move_to(self.circuit.get_center()))
            return 
        self.show_circuit = show_circuit

        self.assemble() 
        self.play(DrawBorderThenFill(self.circuit))
        self.interactive_embed() 
        return

    def update_gate_pos(self): 
        """
        Update the Bounding Boxes for each Gate.

        """
        for gate_id in self.gate_ids:
            # Checking if dictionary contains lists
            # i.e. if this method has already been called
            if not isinstance(self.gate_references[gate_id], list): 
                gate = self.gate_references[gate_id]
            else: 
                gate = self.gate_references[gate_id][0]

            # Update dictionary to contain mobject bbox
            self.gate_references[gate_id] = [
                gate, np.array([gate.get_corner(DL), gate.get_corner(UR)])
            ]
        return

    def render_gate_label(self):
        """ 
        Render gate label in bottom left corner 
        Upon clicking a specific gate, this label will update 
        to the currently selected gate's `gate_id`

        """
        self.gate_label = Text('No Gate Chosen', color=GRAY_C, font_size=30)
        self.gate_label.to_edge(DL) 

        # Let ManiQ know the gate_label is currently being displayed
        self.gate_label_active = True 
        self.play(Write(self.gate_label))

        def update_gate_label():
            """ 
            Checks if cursor is above a specific gate in the Quantum circuit. 
            Is called upon a mouse press and updates the gate id 

            """
            for gate_id, gate_data in self.gate_references.items():
                gate_bbox = np.array(gate_data[1])

                if (gate_bbox[0, 0] <= self.x_manim <= gate_bbox[1, 0] and 
                    gate_bbox[0, 1] <= self.y_manim <= gate_bbox[1, 1]):
        
                    # Update current gate_label with selected gate's gate_id
                    gate_label = Text(gate_id, color=GRAY_C, font_size=30).to_edge(DL)
                    self.remove(self.gate_label)
                    self.add(gate_label)
                    self.gate_label = gate_label # Explicitly replacing -- embed finnicky
            return
        
        # Allow child function to be called explicitly outside parent 
        self.update_gate_label = update_gate_label 
        return

    def render_distribution(self, shots=None, normalize=False, show_labels=False): 
        """ 
        Render calculated statevector from executing displayed circuit on 
        trivial statevector |000...>. 

        """ 
        # Calculate measurement distribution mobject
        self.meas_dist = [ConvertToManim(self.qc).meas_dist(
                shots=shots, 
                normalize=normalize, 
                show_labels=show_labels, 
        )] 

        # Measurement Distribution location in scene
        self.distribution_location = np.array([config.frame_width, 0, 0])
        self.meas_dist[0].move_to(self.distribution_location)

        # Add distribution to scene
        self.add(self.meas_dist[0])
        # Number of displaying distributions 
        self.number_distributions = 1 

        def update_distribution(idx, shots=None, normalize=False, show_labels=False): 
            """
            Recalculates the measurement count/distribution and updates the 
            distribution mobject at the chosen idx.  

            """ 
            # Updated distribution mobject
            meas_dist_update = ConvertToManim(self.qc).meas_dist(
                    shots=shots, 
                    normalize=normalize, 
                    show_labels=show_labels, 
            ).move_to(self.distribution_location)
            meas_dist_update.scale_to_fit_width(self.dist_width*0.8)
            meas_dist_update.move_to([self.dist_locations[idx],0,0])

            # Replace old measurement distribution with new one.
            self.remove(self.meas_dist[idx]) 
            self.add(meas_dist_update) 
            self.meas_dist[idx] = meas_dist_update 
            return

        def show_distribution(): 
            self.play(self.camera.animate.move_to(self.distribution_location))
            return 

        def add_distribution(shots=None, normalize=False, show_labels=False): 
            """
            Adds another distribution to the scene and scales all 
            current distributions to fit within the config frame window. 

            """ 
            # New distribution mobject
            new_dist = ConvertToManim(self.qc).meas_dist(
                shots=shots, 
                normalize=normalize, 
                show_labels=show_labels, 
            )
            self.meas_dist.append(new_dist)

            # Number of displaying distributions 
            num_dists = len(self.meas_dist)
            # Width for each distribution
            self.dist_width = config.frame_width/num_dists

            # central-x locations for each distributoin
            self.dist_locations = [
                config.frame_width/2+self.dist_width*(idx+0.5) for idx in range(num_dists)
            ] 

            # Update all distributions & add new distribution 
            for loc_idx in range(len(self.dist_locations)): 
                self.remove(self.meas_dist[loc_idx])
                self.meas_dist[loc_idx].scale_to_fit_width(self.dist_width*0.8)
                self.meas_dist[loc_idx].move_to([self.dist_locations[loc_idx],0,0])
                self.add(self.meas_dist[loc_idx]) 
            return 

        # Allow update method to be called outside parent 
        self.update_distribution = update_distribution
        self.show_distribution = show_distribution
        self.add_distribution = add_distribution
        return

    def render_density_plot(self, real=True, imag=True): 
        """
        Render density matrix hinton plots calculated from evolving trival 
        statevector through circuit. 

        """ 
        # Real and Imaginary Density Plots
        real_hinton_plot, imag_hinton_plot = ConvertToManim(self.qc).density_matrix_hinton() 

        real_hinton_plot.scale_to_fit_height(config.frame_height * 0.5) 
        imag_hinton_plot.scale_to_fit_height(config.frame_height * 0.5) 
        real_hinton_plot.shift(LEFT*config.frame_width/4).shift(UP*config.frame_height)
        imag_hinton_plot.shift(RIGHT*config.frame_width/4).shift(UP*config.frame_height)

        self.add(real_hinton_plot, imag_hinton_plot)

        def show_density_plot(): 
            self.play(self.camera.animate.move_to([0, config.frame_height, 0]))

        self.show_density_plot = show_density_plot
        return

    def on_mouse_press(self, point, button, modifiers):

        """
        Runs everytime mouse is pressed in pyglet window

        """

        # Get cursor coordinates in manim-space
        self.x_manim, self.y_manim = global_cursor_to_manim(self, 1)

        if hasattr(self, 'gate_label_active'):
            if self.gate_label_active: 
                self.update_gate_pos()
                self.update_gate_label() 

        super().on_mouse_press(point, button, modifiers)
        return 




