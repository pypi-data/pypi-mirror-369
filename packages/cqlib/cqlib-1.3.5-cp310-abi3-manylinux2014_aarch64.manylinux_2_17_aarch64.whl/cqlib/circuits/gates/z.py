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

"""
Defines the Pauli Z gate and Controlled-Z (CZ) gate, fundamental elements
in quantum circuits for phase manipulation.

Classes:
    Z: Pauli Z gate, applies a phase shift of pi to the state `|1>`.
    CZ: Controlled-Z gate, applies a phase shift of pi to the target qubit
    only if the control qubit is in the state `|1>`.
"""
from typing import Optional
import numpy as np

from cqlib.circuits.gates.gate import Gate, ControlledGate


class Z(Gate):
    """
    Pauli Z gate.

    This gate applies a phase shift of pi to the quantum state `|1>`.
    It is represented by the matrix:
    [[ 1, 0 ],
    [ 0, -1 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Pauli Z gate.

        Args:
            label (str | None, optional): An optional label for the Z gate. Defaults to None.
        """
        super().__init__('Z', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the Z gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Z gate.
        """
        return np.array([[1, 0], [0, -1]], dtype=dtype)


class CZ(ControlledGate):
    """
    Controlled-Z (CZ) gate, which is a two-qubit quantum gate.

    This gate applies a phase shift of pi to the target qubit only
    if the control qubit is in the state `|1>`. It is represented by the matrix:
    [[ 1, 0, 0, 0 ],
    [ 0, 1, 0, 0 ],
    [ 0, 0, 1, 0 ],
    [ 0, 0, 0, -1 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the CZ gate.

        Args:
            label (str | None, optional): An optional label for the CZ gate. Defaults to None.
        """
        super().__init__('CZ', 2, control_index=[0],
                         base_gate=Z(), params=[], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the CZ gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 4x4 matrix with complex entries representing the CZ gate.
        """
        return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=dtype)
