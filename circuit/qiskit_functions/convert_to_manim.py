from manim import * 
from qiskit_functions.qiskit_calculations import QiskitCalculations
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix

import itertools

config.preview = True

class ConvertToManim(QiskitCalculations): 
    """ 
    Converts all the calculates done by qiskit into 
    manim mobjects for display. 

    """ 
    def __init__(self, qc): 
        self.qc = qc 

    def statevector(self):
        # Calculate final statevector from evolving the circuit 
        # starting from trivial |000..> 
        sv = self.sv()
        latex_str = sv.draw('latex_source') 
        latex_mobj = MathTex(latex_str, font_size=25, color=GRAY_C)
        return latex_mobj 

    def meas_dist(self, shots=None, normalize=False, show_labels=False): 

        # Calculate measurement distribution 
        dist, counts, shots = self.get_counts(shots=shots)

        bar_labels = [meas_label for meas_label in dist.keys()]
        prob_vals = [meas_prob for meas_prob in dist.values()]
        meas_vals = [meas_val for meas_val in counts.values()]

        if not normalize:
            # Shot count distributoin
            if shots: 
                shot_label = Tex(rf"Shots: {shots}", font_size=40)
            else: 
            # If shots not specified, default to 1000
                shot_label = Tex(rf"Shots: 1000", font_size=40)

            bar_chart = BarChart(
                values=meas_vals, 
                bar_names=bar_labels, 
                x_axis_config={'font_size': 36}
            )
            shot_label.next_to(bar_chart, DOWN)

            if show_labels: 
                bar_labels = bar_chart.get_bar_labels(font_size=40)
                meas_dist = VGroup(bar_chart, bar_labels, shot_label)
            else: 
                meas_dist = VGroup(bar_chart, shot_label) 
        else: 
            # Probability distribution, exact
            y_range = [0, 1, 0.2] 
            bar_chart = BarChart(
                values=prob_vals, 
                bar_names=bar_labels, 
                y_range=y_range, 
                x_axis_config={'font_size': 36}
            )
            shot_label = Tex(rf"Measurement Prob. Distribution", font_size=40)
            shot_label.next_to(bar_chart, DOWN)

            # Show labels above each bar in barchart
            if show_labels:
                bar_labels = bar_chart.get_bar_labels(font_size=40)
                meas_dist = VGroup(bar_chart, bar_labels, shot_label)
            else: 
                meas_dist = VGroup(bar_chart, shot_label)
        return meas_dist 

    def density_matrix_hinton(self):
        # Emulating Qiskit's plot_state_hinton density matrix visualization
        def hinton_size(value, max_size=1.4): 
            return max_size * np.sqrt(abs(value)) 

        def hinton_color(value): 
            return BLUE_C if value >= 0 else GRAY_C

        # Removing any measurement gates from the circuit
        self.qc.data = [
            instruction for instruction in self.qc.data if instruction.operation.name != 'measure'
        ]

        # Density matrix nxn numpy array
        rho = DensityMatrix(self.qc) 
        dm_array = rho.data 

        real_part = dm_array.real 
        imag_part = dm_array.imag

        # Dimension of density matrix
        n = real_part.shape[0] 
        spacing = 1.0 

        # Define the top-left as the 0,0 position of the matrix
        top_left = np.array([-(n-1)/2, (n-1)/2, 0]) 

        # Generate real and imaginary Hinton mobjects
        real_squares = [] 
        imag_squares = []
        for i in range(n): 
            for j in range(n): 
                real_val = real_part[i, j] 
                real_side_len = hinton_size(real_val) 
                real_color = hinton_color(real_val) 

                real_sq = Square(side_length=real_side_len) 
                real_sq.set_fill(real_color, opacity=1.0) 
                real_sq.set_stroke(width=0) 

                real_shift_x = j * spacing
                real_shift_y = -i * spacing 
                real_sq.move_to(top_left + np.array([real_shift_x, real_shift_y, 0]))

                real_squares.append(real_sq)

                imag_val = imag_part[i, j] 
                imag_side_len = hinton_size(imag_val) 
                imag_color = hinton_color(imag_val) 

                imag_sq = Square(side_length=imag_side_len) 
                imag_sq.set_fill(imag_color, opacity=1.0) 
                imag_sq.set_stroke(width=0) 

                imag_shift_x = j * spacing
                imag_shift_y = -i * spacing 
                imag_sq.move_to(top_left + np.array([imag_shift_x, imag_shift_y, 0]))

                imag_squares.append(imag_sq)

        # Background of squares
        real_background = Square(
                side_length=n * spacing, 
                color=BLACK, 
                fill_opacity=1.0,
        ).set_stroke(width=0) 
        real_background.move_to(
            top_left + np.array([(n-1) * spacing / 2, -(n-1) * spacing / 2, 0])
        )
        real_tex = MathTex(rf"Re[\rho]").next_to(real_background, UP)

        imag_background = Square(
                side_length=n * spacing, 
                color=BLACK, 
                fill_opacity=1.0, 
        ).set_stroke(width=0)
        imag_background.move_to(
            top_left + np.array([(n-1) * spacing / 2, -(n-1) * spacing / 2, 0])
        )
        imag_tex = MathTex(rf"Im[\rho]").next_to(imag_background, UP)

        # Axis labels
        def add_axis_labels(n, top_left, spacing, axis_offset=1):
            from itertools import product

            # Generate bit strings for labels
            num_qubits = int(np.log2(n))
            bit_strings = ["".join(seq) for seq in product("01", repeat=num_qubits)]

            # X-axis labels
            x_labels = VGroup()
            for col in range(n):
                label = Text(bit_strings[col], font_size=24)
                label.move_to(top_left + np.array([col*spacing, -(n-1)*spacing-axis_offset, 0]))
                x_labels.add(label)

            # Y-axis labels
            y_labels = VGroup()
            for row in range(n):
                label = Text(bit_strings[row], font_size=24)
                label.move_to(top_left + np.array([-axis_offset, -row * spacing, 0]))
                y_labels.add(label)

            return x_labels, y_labels

        real_x_labels, real_y_labels = add_axis_labels(n, top_left, spacing)
        imag_x_labels, imag_y_labels = add_axis_labels(n, top_left, spacing)

        # Final real and imaginary density matrix Hinton plots
        real_hinton_plot = VGroup(real_background, real_tex, *real_squares, real_x_labels, real_y_labels)
        imag_hinton_plot = VGroup(imag_background, imag_tex, *imag_squares, imag_x_labels, imag_y_labels)

        return real_hinton_plot, imag_hinton_plot


class Tests(Scene):
    def construct(self):
        qc = QuantumCircuit(2)
        qc.h([0, 1])
        qc.cz(0,1)
        qc.ry(np.pi/3 , 0)
        qc.rx(np.pi/5, 1)
        qc.measure_all()
        
        real, imag = ConvertToManim(qc).density_matrix_hinton()
        real.to_edge(LEFT) 
        imag.to_edge(RIGHT)
        self.play(Write(real))
        self.play(Write(imag))

        

        
