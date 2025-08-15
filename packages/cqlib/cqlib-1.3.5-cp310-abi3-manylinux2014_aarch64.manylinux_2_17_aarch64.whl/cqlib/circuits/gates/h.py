# This code is part of cqlib.
#
# Copyright (C) 2024 China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Hadamard gate."""
from typing import Optional
import numpy as np

from cqlib.circuits.gates.gate import Gate
from cqlib.circuits.utils import sqrt2_inv


class H(Gate):
    """
    Hadamard gate.

    The Hadamard gate is a single-qubit gate that creates a superposition state.
    It transforms the basis states `|0⟩` and `|1⟩` into an equal superposition of both states.
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Hadamard gate.

        Args:
            label (str | None, optional): An optional label for the Hadamard gate. Defaults to None.
        """
        super().__init__('H', 1, [], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix representation of the Hadamard gate.

        This method returns the unitary matrix of the Hadamard gate.

         Args:
             dtype (optional): The desired data type for the numpy array. Defaults to np.complex128.

         Returns:
             numpy.ndarray: The unitary matrix of the Hadamard gate.
        """
        return sqrt2_inv * np.array([[1, 1], [1, -1]], dtype=dtype)
