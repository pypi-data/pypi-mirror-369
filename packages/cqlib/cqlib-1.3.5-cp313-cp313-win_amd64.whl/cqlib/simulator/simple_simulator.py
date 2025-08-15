# This code is part of cqlib.
#
# (C) Copyright China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics 2025.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Quantum Circuit Simulator Implementation
"""
from collections import Counter

import numpy as np
from sympy import lambdify

from cqlib import Parameter
from cqlib.circuits.circuit import Circuit

from .simple_sim import TorchBackend, SimpleRunner, gates as simple_gates

try:
    import torch
except ImportError as e:
    pass


# pylint: disable=too-many-instance-attributes
class SimpleSimulator:
    """PyTorch-based quantum circuit simulator.

    This class provides a high-performance quantum circuit simulator using PyTorch
    as the computational backend. It supports both statevector simulation and
    measurement sampling.
    """

    def __init__(
            self,
            circuit: Circuit,
            device: str | int | None = None,
            dtype: type | None = None
    ):
        """Initialize the quantum circuit simulator.

        Args:
            circuit: Quantum circuit to simulate
            device: Computation device ('cpu' or 'cuda')

        Raises:
            ImportError: If PyTorch is not installed
        """
        if torch is None:
            raise ImportError("PyTorch is not installed. `pip install torch` "
                              "Please install it to use the SimpleSimulator. ")
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.circuit = circuit
        self.backend = TorchBackend(device=torch.device(device), dtype=dtype)
        self._runner = SimpleRunner(nq=len(self.circuit.qubits), backend=self.backend)
        self.nq = self._runner.nq
        self._mq = []
        self._state = None
        self._probs = None
        self._measure = None

    def statevector(self, dict_format=True) -> dict[str, complex] | list[complex]:
        """Get the final statevector of the quantum circuit.

        Args:
            dict_format: If True, returns results as dictionary mapping bitstrings to amplitudes
                        If False, returns raw state vector as list.

        Returns:
            dict: {bitstring: complex_amplitude} mapping (e.g. {'00': 0.707+0j, '01': 0+0j})
            list: Raw state vector array [complex_amplitude_0, complex_amplitude_1, ...]
        """
        if self._state is None:
            self._run()
            self._state = self._runner.state()
        state = self.reverse_qubit_order(self._state, self.nq)
        if dict_format:
            return {np.binary_repr(i, width=self.nq): val for i, val in enumerate(state)}
        return state

    def probs(self, dict_format=True) -> dict[str, float] | list[float]:
        """
        Calculate measurement probabilities for all basis states.

        Args:
            dict_format: If True, returns results as dictionary mapping bitstrings to probabilities
                        If False, returns probability array

        Returns:
            dict: {bitstring: probability} mapping (e.g. {'00': 0.5, '01': 0.25, ...})
            list: Probability array [p_00, p_01, p_10, p_11, ...]
        """
        if self._probs is None:
            self.statevector()
            self._probs = self._runner.probs()
        probs = self.reverse_qubit_order(self._probs, self.nq)
        if dict_format:
            return {np.binary_repr(i, width=self.nq): val for i, val in enumerate(probs)}
        return probs

    def measure(self, dict_format=True) -> dict[str, float] | list[float]:
        """
        Get measurement probabilities for measured qubits.

        Args:
            dict_format: If True, returns results as dictionary
                        If False, returns raw probability array

        Returns:
            dict: {bitstring: probability} for measured qubits only
            list: Marginal probability array for measured qubits
        """
        if self._measure is None:
            self.probs()
            self._measure = self._runner.measure(self._mq)
        measure = self.reverse_qubit_order(self._measure, len(self._mq))

        if dict_format:
            return {np.binary_repr(i, width=len(self._mq)): val for i, val in enumerate(measure)}
        return measure

    def sample(
            self,
            shots: int = 100,
            dict_format: bool = True,
    ) -> dict[str, int] | list[str]:
        """
        Sample measurement outcomes from the quantum state.

        Args:
            shots: Number of samples to take
            dict_format: Whether to return as dict

        Returns:
            dict: Measurement counts {bitstring: count} (e.g. {'00': 57, '01': 43})
            str: Concatenated measurement results (e.g. '0001100101...')
        """
        if self._state is None:
            self.statevector()
        samples = self._runner.sample(self._mq, shots)
        if dict_format:
            return {np.binary_repr(int(k), width=len(self._mq))[::-1]: v
                    for k, v in Counter(samples).items()}
        return [np.binary_repr(v, width=len(self._mq))[::-1] for v in samples]

    # pylint: disable=too-many-branches
    def _run(self):
        """Internal method to execute the quantum circuit."""
        for item in self.circuit.circuit_data:
            instr = item.instruction
            if instr.name == 'M':
                self._mq.append(item.qubits[0].index)
            if instr.name in ['I', 'B', 'M']:
                continue
            if instr.params:
                ps = self.params_value_with_gradient(instr.params, self.circuit.parameters_value)
                if instr.name == 'RX':
                    ins_mat = simple_gates.rx_mat(ps[0], self.backend)
                elif instr.name == 'RY':
                    ins_mat = simple_gates.ry_mat(ps[0], self.backend)
                elif instr.name == 'RZ':
                    ins_mat = simple_gates.rz_mat(ps[0], self.backend)
                elif instr.name == 'XY':
                    ins_mat = simple_gates.xy_mat(ps[0], self.backend)
                elif instr.name == 'XY2P':
                    ins_mat = simple_gates.xy2p_mat(ps[0], self.backend)
                elif instr.name == 'XY2M':
                    ins_mat = simple_gates.xy2m_mat(ps[0], self.backend)
                elif instr.name == 'RXY':
                    ins_mat = simple_gates.rxy_mat(ps[0], ps[1], self.backend)
                elif instr.name == 'CRX':
                    ins_mat = simple_gates.crx_mat(ps[0], self.backend)
                elif instr.name == 'CRY':
                    ins_mat = simple_gates.cry_mat(ps[0], self.backend)
                elif instr.name == 'CRZ':
                    ins_mat = simple_gates.crz_mat(ps[0], self.backend)
                elif instr.name == 'U':
                    ins_mat = simple_gates.u_mat(ps[0], ps[1], ps[2], self.backend)
                else:
                    raise ValueError("Unknown gate.")
                getattr(self._runner, instr.name)(
                    *[q.index for q in item.qubits],
                    mat=ins_mat
                )
            else:
                getattr(self._runner, instr.name)(
                    *[q.index for q in item.qubits],
                    mat=np.asarray(instr)
                )

    def params_value_with_gradient(
            self,
            params: list[Parameter | float | complex | int],
            parameters_value: dict[Parameter, float | int]
    ):
        """Evaluate parameter expressions with gradient support.

        Args:
            params: List of parameters/expressions to evaluate
            parameters_value: Mapping of parameter values

        Returns:
            list: Evaluated parameter values
        """
        values = []
        for p in params:
            if isinstance(p, Parameter):
                expr = p.symbol
                base_params = [param for param in expr.free_symbols
                               if Parameter(str(param)) in parameters_value]
                param_dict = {str(sym): parameters_value[Parameter(str(sym))]
                              for sym in base_params}
                func = lambdify(base_params, expr, modules=self._torch_wrapper())
                tensor_args = [param_dict[str(sym)] for sym in base_params]
                value = func(*tensor_args)
                tensor_val = self.backend.as_tensor(value)
            else:
                tensor_val = self.backend.as_tensor(p)
            values.append(tensor_val)
        return values

    def _torch_wrapper(self):
        """Create function mapping from sympy to PyTorch operations.

        Returns:
            dict: Mapping of sympy functions to PyTorch operations
        """
        return {
            'sin': self.backend.sin,
            'cos': self.backend.cos,
            'exp': self.backend.exp,
            'sqrt': self.backend.sqrt,
            'add': self.backend.add,
            'mul': self.backend.mul
        }

    @staticmethod
    def reverse_qubit_order(list_value, num_qubits):
        """
        Reverse the order of qubits in a list.

        Args:
            list_value: List of values to reverse
            num_qubits: Number of qubits

        Returns:
            list: Reversed list of values
        """
        indices = torch.arange(2 ** num_qubits)
        reversed_indices = torch.zeros_like(indices)

        for i in range(num_qubits):
            reversed_indices |= ((indices >> i) & 1) << (num_qubits - 1 - i)

        return list_value[reversed_indices]
