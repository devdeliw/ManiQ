from qiskit import ClassicalRegister, QuantumCircuit, transpile 
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
from qiskit.primitives import Sampler

class QiskitCalculations: 
    """ 
    Class to perform all general functions on a QuantumCircuit object. 
    This includes:
        - Running a circuit on a trivial statevector
        - Returning measurement probabilities 
        - Returning resultant statevectors/density matrices

    """

    def __init__(self, qc):
        self.qc = qc 

    def sv(self): 
        """ 
        Runs the circuit and returns the final statevector. 

        """
        
        self.qc.data = [instr for instr in self.qc.data if instr.operation.name != "measure"]
        simulator = Aer.get_backend('statevector_simulator')
        transpiled_qc = transpile(self.qc, simulator) 
        job = simulator.run(transpiled_qc).result()

        sv = job.get_statevector(transpiled_qc) 
        return sv
    
    def get_counts(self, shots=None): 
        """ 
        Runs the circuit and outputs the measurement probabilities.
        Uses sampler primitive. 

        """ 

        def add_missing_measurements(qc):
            
            num_qubits = qc.num_qubits 

            # Ensuring classical register exists for measurement gates
            if not qc.cregs: 
                classical_reg = ClassicalRegister(num_qubits, 'c')
                qc.add_register(classical_reg) 

            # Finding which qubits already have measurement gates
            measured_qubits = set() 
            for instruction in qc.data:
                if instruction.operation.name == 'measure': 
                    measured_idxs = [qc.find_bit(qubit).index for qubit in instruction.qubits]
                    for idx in measured_idxs: 
                        measured_qubits.add(idx)

            # Adds measurement gate to first quantum register
            qc.barrier()
            for qubit in range(num_qubits): 
                if qubit not in measured_qubits: 
                    qc.measure(qubit, qc.cregs[0][qubit])
            return qc

        # Add missing measurement gates, if any
        add_missing_measurements(self.qc)

        # Initialize Sampler Primitive
        sampler = Sampler()

        # Run simulation (exact if counts not specified)
        result = sampler.run([self.qc], shots=shots).result()
        dist = result.quasi_dists[0] 
        dist = {bin(qubit_idx)[2:]: val for qubit_idx, val in dist.items()}

        # If shots not specified, set shots=1000
        if not shots: 
            shots = 1000
        
        counts = {qubit_idx: val * shots for qubit_idx, val in dist.items()}
         
        return dist, counts, shots





    



