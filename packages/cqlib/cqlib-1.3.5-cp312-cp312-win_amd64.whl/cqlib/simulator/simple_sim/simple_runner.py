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
Quantum Circuit Simulator Runner
"""

# pylint: disable=invalid-name
import numpy as np

from .torch_backend import TorchBackend


# pylint: disable=too-many-public-methods
class SimpleRunner:
    """
    A simple quantum circuit simulator using tensor operations.
    """

    def __init__(self, nq: int, backend: TorchBackend) -> None:
        """Initialize the quantum circuit simulator.

        Args:
           nq: Number of qubits in the circuit
           backend: Computational backend for tensor operations
        """
        self.backend = backend
        self.nq = nq
        self._state = backend.zeros(2 ** nq)
        self._state[0] = 1.0 + 0j
        self._shape = [2 for _ in range(self.nq)]
        self._state = self.backend.reshape(self._state, self._shape)

    def _inv_subscripts(self, subscripts: list[int]) -> list[int]:
        """
        Compute inverse permutation of qubit indices.

        Args:
            subscripts: List of permuted indices

        Returns:
            List of inverse permutation indices
        """
        subscripts = np.asarray(subscripts)
        inv = np.empty_like(subscripts)
        inv[subscripts] = np.arange(subscripts.shape[0])
        return inv.tolist()

    def H(self, i: int, mat: np.ndarray):
        """Apply Hadamard gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def X(self, i: int, mat: np.ndarray):
        """Apply Pauli-X gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def Y(self, i: int, mat: np.ndarray):
        """Apply Pauli-Y gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def Z(self, i: int, mat: np.ndarray):
        """Apply Pauli-Z gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def S(self, i: int, mat: np.ndarray):
        """Apply S gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def T(self, i: int, mat: np.ndarray):
        """Apply T gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def SD(self, i: int, mat: np.ndarray):
        """Apply s dg gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def TD(self, i: int, mat: np.ndarray):
        """Apply T dg gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def RX(self, i: int, mat: np.ndarray):
        """Apply rotation around X-axis gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def RY(self, i: int, mat: np.ndarray):
        """Apply rotation around Y-axis gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def RZ(self, i: int, mat: np.ndarray):
        """Apply rotation around Z-axis gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def XY(self, i: int, mat: np.ndarray):
        """Apply rotation around Z-axis gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def XY2P(self, i: int, mat: np.ndarray):
        """Apply rotation around the X-axis by pi/2,
        modulated by a phase theta around the Y-axis."""
        return self.apply_single_qubit_gate(i, mat)

    def XY2M(self, i: int, mat: np.ndarray):
        """Apply rotation around the X-axis by -pi/2,
        modulated by a phase theta around the Y-axis."""
        return self.apply_single_qubit_gate(i, mat)

    def RXY(self, i: int, mat: np.ndarray):
        """Apply rotation around Z-axis gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def X2M(self, i: int, mat: np.ndarray):
        """Apply X/2 (π/2 rotation around X-axis) gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def X2P(self, i: int, mat: np.ndarray):
        """Apply inverse X/2 (-π/2 rotation around X-axis) gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def Y2M(self, i: int, mat: np.ndarray):
        """Apply Y/2 (π/2 rotation around Y-axis) gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def Y2P(self, i: int, mat: np.ndarray):
        """Apply inverse Y/2 (-π/2 rotation around Y-axis) gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def U(self, i: int, mat: np.ndarray):
        """Apply U gate to qubit i."""
        return self.apply_single_qubit_gate(i, mat)

    def apply_single_qubit_gate(self, i: int, mat: np.ndarray):
        """
        Apply arbitrary single-qubit gate to specified qubit.

        Args:
            i: Target qubit index
            mat: 2x2 unitary matrix representing the gate

        Returns:
            self for method chaining
        """
        subscripts = list(range(self.nq))
        subscripts.remove(i)
        subscripts = [i] + subscripts
        self._state = self.backend.reshape(
            self.backend.permute(self._state, subscripts), (2, -1)
        )
        self._state = self.backend.matmul(
            self.backend.reshape(mat, (2, 2)),
            self._state
        )
        self._state = self.backend.permute(
            self.backend.reshape(self._state, self._shape),
            self._inv_subscripts(subscripts),
        )
        return self

    def CX(self, i: int, j: int, mat: np.ndarray):
        """Apply controlled-X (CNOT) gate with control i and target j."""
        return self.apply_two_qubit_gate(i, j, mat)

    def CY(self, i: int, j: int, mat: np.ndarray):
        """Apply controlled-Y gate with control i and target j."""
        return self.apply_two_qubit_gate(i, j, mat)

    def CZ(self, i: int, j: int, mat: np.ndarray):
        """Apply controlled-Z gate with control i and target j."""
        return self.apply_two_qubit_gate(i, j, mat)

    def CRX(self, i: int, j: int, mat: np.ndarray):
        """Apply controlled rotation around X-axis gate."""
        return self.apply_two_qubit_gate(i, j, mat)

    def CRY(self, i: int, j: int, mat: np.ndarray):
        """Apply controlled rotation around Y-axis gate."""
        return self.apply_two_qubit_gate(i, j, mat)

    def CRZ(self, i: int, j: int, mat: np.ndarray):
        """Apply controlled rotation around Z-axis gate."""
        return self.apply_two_qubit_gate(i, j, mat)

    def SWAP(self, i: int, j: int, mat: np.ndarray):
        """Apply SWAP gate."""
        return self.apply_two_qubit_gate(i, j, mat)

    def apply_two_qubit_gate(self, i: int, j: int, mat: np.ndarray):
        """Apply arbitrary two-qubit gate to specified qubits.

        Args:
            i: Control qubit index
            j: Target qubit index
            mat: 4x4 unitary matrix representing the gate

        Returns:
            self for method chaining
        """
        subscripts = list(range(self.nq))
        subscripts.remove(i)
        subscripts.remove(j)
        subscripts = [i, j] + subscripts

        self._state = self.backend.reshape(
            self.backend.permute(self._state, subscripts), (4, -1)
        )
        self._state = self.backend.matmul(
            self.backend.reshape(mat, (4, 4)), self._state
        )

        self._state = self.backend.permute(
            self.backend.reshape(self._state, self._shape),
            self._inv_subscripts(subscripts),
        )
        return self

    def CCX(self, i: int, j: int, k: int, mat: np.ndarray):
        """Apply CCX gate."""
        return self.apply_three_qubit_gate(i, j, k, mat)

    def apply_three_qubit_gate(self, i: int, j: int, k: int, mat: np.ndarray):
        """Apply arbitrary three-qubit gate to specified qubits.

        Args:
            i: First control qubit index
            j: Second control qubit index
            k: Target qubit index
            mat: 8x8 unitary matrix representing the gate (e.g., CCX/Toffoli)

        Returns:
            self for method chaining
        """
        # Reorder qubits so that i, j, k are the first three dimensions
        subscripts = list(range(self.nq))
        subscripts.remove(i)
        subscripts.remove(j)
        subscripts.remove(k)
        subscripts = [i, j, k] + subscripts  # Bring i, j, k to the front

        # Reshape state into (8, -1) to apply the 8x8 gate
        self._state = self.backend.reshape(
            self.backend.permute(self._state, subscripts), (8, -1))

        # Apply the gate (mat is 8x8)
        self._state = self.backend.matmul(mat, self._state)

        # Reshape back and restore original qubit order
        self._state = self.backend.reshape(self._state, self._shape)
        self._state = self.backend.permute(
            self._state,
            self._inv_subscripts(subscripts)  # Inverse permutation
        )
        return self

    def state(self):
        """Get the current state vector as a flattened tensor.

        Returns:
            torch.Tensor: Flattened state vector
        """
        return self.backend.ravel(self._state)

    def probs(self):
        """Compute measurement probabilities for all basis states.

        Returns:
            torch.Tensor: Probability distribution over computational basis
        """
        state = self.state()
        return self.backend.real(self.backend.conj(state) * state)

    def measure(self, mq: list[int]):
        """Compute measurement probabilities for specified qubits.

        Args:
            mq: List of qubit indices to measure

        Returns:
            torch.Tensor: Marginal probability distribution

        Raises:
            ValueError: If specified qubits are invalid
        """
        mq = list(mq)
        idx = list(range(self.nq))
        try:
            for i in mq:
                idx.remove(i)
        except ValueError as e:
            raise ValueError("Make sure qubits to be measured are correct.") from e
        idx = mq + idx

        probs = self.probs().reshape([2 for _ in range(self.nq)])

        return self.backend.real(
            self.backend.sum(
                self.backend.reshape(
                    self.backend.permute(probs, idx), [2 ** len(mq), -1]
                ),
                axis=1,
            )
        )

    def sample(
            self,
            mq: list[int],
            shots: int = 100,
    ):
        """Sample measurement outcomes from the quantum state.

        Args:
            mq: List of qubit indices to measure
            shots: Number of samples to take
            is_sorted: Whether to sort results by bitstring
            dict_format: Whether to return as dict (else string)

        Returns:
            dict/str: Measurement results as counts or concatenated strings
        """
        p = np.real(self.backend.to_numpy(self.measure(mq)))
        p_norm = p / np.sum(p)
        r = np.random.choice(2 ** len(mq), shots, p=p_norm)
        return r
