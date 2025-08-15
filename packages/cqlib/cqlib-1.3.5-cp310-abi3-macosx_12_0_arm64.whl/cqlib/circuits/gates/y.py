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
Defines the Pauli Y gate and its variants: Y2P (rotations around the y-axis by pi/2)
and Y2M (rotations around the y-axis by -pi/2).

Classes:
    Y: Pauli Y gate, acts as a quantum bit flip and phase shift gate.
    Y2P: Performs a rotation around the y-axis by pi/2.
    Y2M: Performs a rotation around the y-axis by -pi/2.
"""
import math
from typing import Optional, Sequence
import numpy as np

from cqlib.circuits.gates.gate import Gate, ControlledGate
from cqlib.circuits.utils import sqrt2_inv


class Y(Gate):
    """
    Pauli Y gate.

    This gate acts as both a bit flip and a phase shift on a qubit.
    It is represented by the matrix:
    [[ 0, -i ],
    [ i, 0 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Pauli Y gate.

        Args:
            label (str | None, optional): An optional label for the Y gate. Defaults to None.
        """
        super().__init__('Y', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the Y gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Y gate.
        """
        return np.array([[0, -1j], [1j, 0]], dtype=dtype)


class CY(ControlledGate):
    """
    CY gate.

    This gate acts as both a bit flip and a phase shift on a qubit.
    It is represented by the matrix:
    [[ 1, 0, 0, 0],
     [ 0, 0, 0, -i],
     [ 0, 0, 1, 0],
     [ 0, i, 0, 0]]
    """
    is_supported_by_qcis = False

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the CY gate.

        Args:
            label (str | None, optional): An optional label for the CY gate. Defaults to None.
        """
        super().__init__('CY', 2, control_index=[0],
                         base_gate=Y(), params=[], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the Y gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Y gate.
        """
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, -1j],
            [0, 0, 1j, 0],
        ], dtype=dtype)

    def to_qcis(self, qubits: Sequence) -> list:
        """
        Convert the CY gate to a sequence of QCIS instructions.

        Args:
            qubits (list | tuple): The list or tuple of qubits the gate acts on.
                It requires exactly three qubits.
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.circuits.gates.z import CZ
        from cqlib.circuits.gates.rz import RZ
        from cqlib.circuits.instruction_data import InstructionData

        control_qubit, target_qubit = self._parse_qubits(qubits)
        return [
            InstructionData(RZ(math.pi / 2), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
            InstructionData(CZ(), [control_qubit, target_qubit]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(-math.pi / 2), [target_qubit]),
        ]


class Y2P(Gate):
    """
    Y2P gate performs a rotation around the y-axis of the Bloch sphere by pi/2.

    This rotation is useful for creating specific quantum states or for quantum state manipulation.
    It is represented by the matrix:
    sqrt(1/2) * [[ 1, -1 ], [ 1, 1 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Y2P gate.

        Args:
            label (str | None, optional): An optional label for the Y2P gate. Defaults to None.
        """
        super().__init__('Y2P', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the Y2P gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Y2P gate.
        """
        return sqrt2_inv * np.array([[1, -1], [1, 1]], dtype=dtype)


class Y2M(Gate):
    """
    Y2M gate performs a rotation around the Y-axis of the Bloch sphere by -pi/2.

    This rotation is useful for undoing specific quantum operations or preparing quantum states.
    It is represented by the matrix:
    sqrt(1/2) * [[ 1, 1 ], [ -1, 1 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Y2M gate.

        Args:
            label (str | None, optional): An optional label for the Y2M gate. Defaults to None.
        """
        super().__init__('Y2M', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the Y2M gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Y2M gate.
        """
        return sqrt2_inv * np.array([[1, 1], [-1, 1]], dtype=dtype)
