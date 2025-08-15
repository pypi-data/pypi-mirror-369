# This code is part of cqlib.
#
# (C) Copyright China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Statevector simulator.


Note:
The measurement results are returned in reverse order of the qubits.
For example, if the circuit includes measurements:

```
c = Circuit([0, 1])
c.x(0)
c.measure_all()

sim = StatevectorSimulator(circuit=c)
print(sim.probs())
```
# {'00': 0.0, '01': 1.0, '10': 0.0, '11': 0.0}

The results will be returned in the order of Q1, Q0.
"""

import ctypes
import time
from collections import Counter

import numpy as np

from cqlib.circuits.circuit import Circuit
from cqlib.circuits.parameter import Parameter
from cqlib.exceptions import CqlibError
from cqlib.simulator.mergy import Gate, merge_gate

from cqlib.simulator.statevector_simulator_c import get_state, get_probs, get_measure, get_sample

gate_name_map = {
    "H": 72,
    "X": 88,
    "Y": 89,
    "Z": 90,
    "S": 83,
    "T": 84,
    "SD": 8368,
    "TD": 8468,
    "X2M": 885077,
    "X2P": 885080,
    "Y2M": 895077,
    "Y2P": 895080,
    "CX": 6788,
    "CY": 6789,
    "CZ": 6790,
    "RX": 8288,
    "RY": 8289,
    "RZ": 8290,
    "U3": 8551,
    "U": 8551,
    "fgate": 102,
    "XY": 8889,
    "XY2M": 88895077,
    "XY2P": 88895080,
    "RXY": 828889,
    "CCX": 102,
    "SWAP": 102,
    "CRX": 102,
    "CRY": 102,
    "CRZ": 102,
    "custom_gate": 102,
}


class StatevectorSimulator:
    """
    StatevectorSimulator is a quantum circuit simulator that simulates quantum circuits
    based on the state vector representation.
    """

    def __init__(
            self,
            circuit: Circuit,
            is_fusion: bool = False,
            fusion_max_qubit: int = 5,
            omp_threads: int = 0,
            fusion_th: int = 15,
    ):
        """
        Initializes the statevector simulator.

        Args:
            circuit (Circuit): The quantum circuit to be simulated.
            is_fusion (bool): Whether to apply gate fusion optimization (default: True).
            fusion_max_qubit (int): Maximum number of qubits for fusion (default: 5).
            omp_threads (int): Number of threads for parallel processing (default: 0).
            fusion_th (int): Number of qubits above which gate fusion is applied (default: 15).
        """
        if omp_threads < 0:
            raise ValueError('')
        self.circuit = circuit
        self.is_fusion = is_fusion
        self.fusion_max_qubit = fusion_max_qubit
        self.omp_threads = omp_threads
        self.fusion_th = fusion_th
        self._fusion_applied = False

        self.nq = len(circuit.qubits)
        self.dim: int = 2 ** self.nq
        self.gates = []
        self.measure_qubits = []
        self.qubit_mapping = {q: i for i, q in enumerate(circuit.qubits)}
        self._parse_circuit()
        self.state_ptr_capsule = None
        self.probs_ptr_capsule = None
        self.measure_ptr_capsule = None
        self.samples_ptr_capsule = None

    def _parse_circuit(self):
        """
        Parses the quantum circuit and prepares the list of gates to be simulated.
        It extracts the qubits and parameters from each gate in the circuit.
        """
        for item in self.circuit.instruction_sequence:
            qubits = [self.qubit_mapping.get(q) for q in item.qubits]

            if item.instruction.name in ['I', 'B']:
                continue
            if item.instruction.name == 'M':
                self.measure_qubits.extend(qubits)
                continue
            ps = []
            for param in item.instruction.params:
                if isinstance(param, Parameter):
                    param = float(param.value(params=self.circuit.parameters_value))
                ps.append(param)
            item.instruction.params = ps
            name = item.instruction.name

            self.gates.append(Gate(
                name=name,
                qubits=qubits,
                theta=ps,
                mat=np.asarray(item.instruction)
            ))

    def _check_fusion(self):
        """
        Applies gate fusion optimization if applicable, based on the number of qubits
        and the fusion threshold. This reduces the complexity of simulating large circuits.
        """
        if self.is_fusion and not self._fusion_applied:
            assert len(self.gates) != 0
            if self.nq >= self.fusion_th:  # default larger then 15 qubits
                self.gates = merge_gate(self.gates, max_qubit=self.fusion_max_qubit)
                self._fusion_applied = True  # dont fuse again

    @staticmethod
    def _check_errcode(errcode: int):
        """
        Checks the error code returned from the C library and raises the appropriate exception.

        Args:
            errcode (int): Error code returned from the C function.

        Raises:
            RuntimeError: If the error code corresponds to an invalid gate or memory allocation error.
        """
        match errcode:
            case 0:  # no error
                pass
            case 1:
                raise RuntimeError("Invalid gate.")
            case 2:
                raise RuntimeError("Memory allocation error.")
            case _:
                raise RuntimeError(f"Unknown error code `{errcode}`.")

    def statevector(self) -> dict:
        """
        Returns the current state vector of the quantum circuit after simulation.
        This function ignores measurement gates (i.e., 'M' gates) during the simulation.

        Returns:
            np.ndarray: The state vector representing the quantum state.
        """
        self._check_fusion()
        gates_list = self.get_gates()
        state_list, state_ptr_capsule = get_state(self.nq, 2 ** self.nq, gates_list, self.omp_threads)
        self.state_ptr_capsule = state_ptr_capsule
        state = {np.binary_repr(i, width=self.nq): val for i, val in enumerate(state_list)}
        return state

    def probs(self) -> dict[str, np.float64]:
        """
        Calculates the probabilities of measuring each possible state of the quantum circuit.
        This function ignores measurement gates (i.e., 'M' gates) during the simulation.

        Returns:
            np.ndarray: A list of probabilities for each possible outcome.
        """
        self._check_fusion()
        if self.state_ptr_capsule is None:
            self.statevector()
        probs_array, probs_ptr_capsule = get_probs(self.nq, 2 ** self.nq, self.omp_threads, self.state_ptr_capsule)
        self.probs_ptr_capsule = probs_ptr_capsule
        return {np.binary_repr(i, width=self.nq): val for i, val in enumerate(probs_array)}

    def measure(self) -> np.array:
        """
        Measures the quantum circuit's state on the specified qubits or all qubits if no specific qubits
        are selected. Returns the probability distribution of the measurement outcomes.

        Returns:
            np.ndarray: A probability distribution of the measurement results.
        """
        self._check_fusion()
        if self.probs_ptr_capsule is None:
            self.probs()

        if not self.measure_qubits:  # all measured
            raise CqlibError("Measured qubits are empty, please add measurement gates first.")

        mq_ordered = sorted(self.measure_qubits.copy())
        # Call get_measure from the C extension module
        measure_array, measure_ptr_capsule = get_measure(
            self.nq,
            self.omp_threads,
            self.measure_qubits,
            mq_ordered,
            self.probs_ptr_capsule
        )
        self.measure_ptr_capsule = measure_ptr_capsule
        return {np.binary_repr(i, width=len(self.measure_qubits)): val for i, val in enumerate(measure_array)}

    def sample(
            self,
            shots: int = 1024,
            is_sorted: bool = False,
            sample_block_th: int = 10,
            is_raw_data: bool = False,
            rng_seed: int = None
    ) -> np.ndarray | dict[str, int]:
        """
        Samples the quantum circuit multiple times, returning either the raw sampled data or a
        frequency distribution of the measurement outcomes.

        Args:
            shots (int): Number of times to sample the circuit (default: 1024).
            is_sorted (bool): Whether to return the results sorted by state (default: False).
            sample_block_th (int): Block threshold for sampling optimization (default: 10).
            is_raw_data (bool): If True, returns raw sample data instead of a frequency dictionary (default: False).
            rng_seed (int): Seed for the random number generator (default: None).

        Returns:
            np.ndarray | dict[str, int]: The sampled results, either as raw data or as a frequency distribution.
        """
        if not self.measure_qubits:  # all qubits measured
            self.measure_qubits = list(range(self.nq))
        assert shots < 4294967296  # uint32_t

        if self.measure_ptr_capsule is None:
            # If measure_ptr_capsule doesn't exist, perform measurement first
            self.measure()

        if rng_seed is None:
            rng_seed = int(time.time())

        # Call get_sample from the C extension module
        samples_array, samples_ptr_capsule = get_sample(
            shots,
            len(self.measure_qubits),
            self.measure_ptr_capsule,
            self.omp_threads,
            self.nq,
            sample_block_th,
            rng_seed
        )
        # Store samples_ptr_capsule to keep the samples_ptr alive
        self.samples_ptr_capsule = samples_ptr_capsule

        # Check if samples_array is None
        if samples_array is None:
            raise RuntimeError("Failed to get samples from the simulator.")

        if is_raw_data:
            return samples_array

        mq_len = len(self.measure_qubits)
        counts = Counter(samples_array)
        # Convert counts to binary strings
        result = {
            np.binary_repr(int(k), width=mq_len): v for k, v in counts.items()
        }
        if is_sorted:
            result = dict(sorted(result.items()))
        return result

    def get_gates(self) -> list[dict]:
        """
        Retrieves detailed information about all gates in the current quantum circuit.
        """
        gates_list = []
        for gate in self.gates:
            gate_dict = {
                'gate_id': gate_name_map[gate.name],
                'qubits': gate.qubits,
            }
            if gate.theta:
                gate_dict['theta'] = gate.theta
            if gate.mat is not None:
                mat_list = [complex(val) for val in gate.mat.flatten()]
                gate_dict['mat'] = mat_list
            gates_list.append(gate_dict)
        return gates_list
