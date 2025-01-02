from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import CircuitInstruction, Clbit, Instruction, Qubit
from random_circuit import random_circuit

import pandas as pd 
import json


qc = random_circuit(5, depth=5, measure=True)

class CircuitUpdate: 
    """ 
    Class for converting ManiQ circuit back into qiskit QuantumCircuit object.

    Updated ManiQ Circuit
            ↓
    Updated DataFrame
            ↓
    Updated QuantumCircuit Instructions
            ↓
    Updated QuantumCircuit

    """

    def __init__(self, circuit_data): 
        """ 
        Args: 
            circuit_data (pandas DataFrame): contains information for ManiQ Circuit. 

        """
        self.circuit_data = circuit_data 
    
    def data_to_instruction(self):
        """ 
        Converts Circuit DataFrame into pseudo-Qiskit QuantumCircuitData object. 

        """

        # Get the minimum # of qubits and clbits of circuit
        num_qbits, num_cbits = 0, 0
        for qbits in self.circuit_data['qbits']:
            for qbit in qbits: 
                if qbit > num_qbits: 
                    num_qbits = qbit
        for cbits in self.circuit_data['cbits']: 
            for cbit in cbits: 
                if cbit > num_cbits: 
                    num_cbits = cbit

        self.num_qubits = num_qbits+1
        self.num_clbits = num_cbits+1

        # Initialize circuit instruction list
        circuit_instructions = []
        for _, element in self.circuit_data.iterrows(): 
            name = element['qiskit_names'] 
            qbits = element['qbits']
            cbits = element['cbits']
            params = element['params']

            operation = Instruction(
                name=name, 
                num_qubits=len(qbits), 
                num_clbits=len(cbits), 
                params=params, 
            )


            qr = QuantumRegister(self.num_qubits, 'q')
            cr = ClassicalRegister(self.num_clbits, 'c')
            qubits = tuple(Qubit(qr, qbit) for qbit in qbits)
            clbits = tuple(Clbit(cr, cbit) for cbit in cbits)

            circuit_instructions.append(
                CircuitInstruction(
                    operation=operation,
                    qubits=qubits, 
                    clbits=clbits, 
                ),
            ) 

        return circuit_instructions 
    
    def update_circuit(self):
        """ 
        Converts a QuantumCircuitData instructions into a QuantumCircuit object. 

        Args: 
            circuit_instructions (qiskit QuantumCircuitData): set of instructions from 
            QuantumCircuit().data. 

        """

        circuit_instructions = self.data_to_instruction()

        qc = QuantumCircuit(self.num_qubits, self.num_clbits)
        
        for instruction in circuit_instructions:
            gate_name = instruction.operation.name
            qbits = [qc.find_bit(qubit).index for qubit in instruction.qubits]
            cbits = [qc.find_bit(clbit).index for clbit in instruction.clbits]
            params = instruction.operation.params
            
            if params:
                if cbits:
                    getattr(qc, gate_name)(*params, *qbits, *cbits)
                else:
                    getattr(qc, gate_name)(*params, *qbits)
            else:
                if cbits:
                    getattr(qc, gate_name)(*qbits, *cbits)
                else:
                    getattr(qc, gate_name)(*qbits)
        
        return qc




