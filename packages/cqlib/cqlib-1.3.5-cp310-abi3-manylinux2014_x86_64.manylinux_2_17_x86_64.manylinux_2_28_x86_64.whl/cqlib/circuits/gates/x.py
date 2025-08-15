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
Defines the Pauli X gate and its variants:
    X2P (rotations around the x-axis by pi/2),
    X2M (rotations around the x-axis by -pi/2).
    Also includes the controlled versions CX (Controlled-X),
    CCX (Controlled-CX, also known as Toffoli gate).

Classes:
    X: Pauli X gate, acts as a quantum NOT gate.
    CX: Controlled-X gate (CNOT), flips the target qubit if the control
    qubit is in the state `|1>`.
    CCX: Controlled-CX gate (Toffoli gate), flips the target qubit if
    both control qubits are in the state `|1>`.
    X2P: Rotates around the x-axis of the Bloch sphere by pi/2.
    X2M: Rotates around the x-axis of the Bloch sphere by -pi/2.
"""
import math
from typing import Type, Optional, Sequence

import numpy as np

from cqlib.circuits.gates.gate import Gate, ControlledGate
from cqlib.circuits.utils import sqrt2_inv


class X(Gate):
    """
    Pauli X gate.

    This gate acts as a quantum NOT gate, flipping the state of a qubit.
    It is represented by the matrix:
    [[ 0, 1 ],
    [ 1, 0 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Pauli X gate.

        Args:
            label (str | None, optional): An optional label for the X gate. Defaults to None.
        """
        super().__init__('X', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the X gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the X gate.
        """
        return np.array([[0, 1], [1, 0]], dtype=dtype)


class CX(ControlledGate):
    """
    Controlled-X gate, which is a two-qubit quantum gate.

    Also known as the CNOT gate, it flips the target qubit if the control
    qubit is in the state `|1>`.

    It is represented by the matrix:
    [[ 1, 0, 0, 0 ],
    [ 0, 1, 0, 0 ],
    [ 0, 0, 0, 1 ],
    [ 0, 0, 1, 0 ]]
    """
    is_supported_by_qcis = False

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the CX gate.

        Args:
            label (str | None, optional): An optional label for the CX gate. Defaults to None.
        """
        super().__init__(
            'CX',
            2,
            control_index=[0],
            base_gate=X(),
            params=[],
            label=label
        )

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the CX gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 4x4 matrix with complex entries representing the CX gate.
        """
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=dtype)

    def to_qcis(self, qubits: Sequence) -> list:
        """
        Convert the CX gate to a sequence of QCIS instructions.

        Args:
            qubits (list | tuple): The list or tuple of qubits the gate acts on.
                It requires exactly two qubits.

        Returns:
            list: A list of InstructionData objects representing the CX gate in QCIS.

        Raises:
            ValueError: If the number of qubits is not exactly two.
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.circuits.gates.h import H
        from cqlib.circuits.gates.z import CZ
        from cqlib.circuits.instruction_data import InstructionData

        control_qubit, target_qubit = self._parse_qubits(qubits)
        return [
            InstructionData(H(), [target_qubit]),
            InstructionData(CZ(), [control_qubit, target_qubit]),
            InstructionData(H(), [target_qubit]),
        ]


CNOT = CX


class CCX(ControlledGate):
    """
    Controlled-CX gate, which is a three-qubit quantum gate.

    Also known as the Toffoli gate, it flips the target qubit
    if both control qubits are in the state `|1>`.

    It is represented by the matrix:
    [[ 1, 0, 0, 0, 0, 0, 0, 0 ],
    [ 0, 1, 0, 0, 0, 0, 0, 0 ],
    [ 0, 0, 1, 0, 0, 0, 0, 0 ],
    [ 0, 0, 0, 1, 0, 0, 0, 0 ],
    [ 0, 0, 0, 0, 1, 0, 0, 0 ],
    [ 0, 0, 0, 0, 0, 1, 0, 0 ],
    [ 0, 0, 0, 0, 0, 0, 0, 1 ],
    [ 0, 0, 0, 0, 0, 0, 1, 0 ]]
    """
    is_supported_by_qcis = False

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the CCX gate.

        Args:
            label (str | None, optional): An optional label for the CCX gate.
                Defaults to None.
        """
        super().__init__('CCX', 3, control_index=[0, 1],
                         base_gate=X(), params=[], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the CCX gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: An 8x8 matrix with complex entries representing the CCX gate.
        """
        return np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0],
        ], dtype=dtype)

    def to_qcis(self, qubits: Sequence) -> list:
        """
        Convert the CCX gate to a sequence of QCIS instructions.

        Args:
            qubits (list | tuple): The list or tuple of qubits the gate acts on.
                It requires exactly three qubits.

        Returns:
            list: A list of InstructionData objects representing the CCX gate in QCIS.

        Raises:
            ValueError: If the number of qubits is not exactly three.
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.circuits.gates.z import CZ
        from cqlib.circuits.gates.rz import RZ
        from cqlib.circuits.gates.y import Y2P, Y2M
        from cqlib.circuits.instruction_data import InstructionData

        control_qubit_0, control_qubit_1, target_qubit = self._parse_qubits(qubits)
        return [
            InstructionData(CZ(), [control_qubit_1, target_qubit]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(-math.pi / 4), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),

            InstructionData(CZ(), [control_qubit_0, target_qubit]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(math.pi / 4), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),

            InstructionData(CZ(), [control_qubit_1, target_qubit]),
            InstructionData(RZ(math.pi * 5 / 4), [control_qubit_1]),
            InstructionData(Y2P(), [control_qubit_1]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(-math.pi / 4), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),

            InstructionData(CZ(), [control_qubit_0, target_qubit]),
            InstructionData(CZ(), [control_qubit_0, control_qubit_1]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(math.pi / 4), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
            InstructionData(Y2M(), [control_qubit_1]),
            InstructionData(RZ(-math.pi / 4), [control_qubit_1]),
            InstructionData(Y2P(), [control_qubit_1]),
            InstructionData(RZ(math.pi / 4), [control_qubit_0]),

            InstructionData(CZ(), [control_qubit_0, control_qubit_1]),
            InstructionData(Y2M(), [control_qubit_1]),
            InstructionData(RZ(math.pi), [control_qubit_1]),
        ]


CCNOT: Type[CCX] = CCX


class X2P(Gate):
    """
    Implements the X2P gate, which applies a rotation around the x-axis of the Bloch sphere by pi/2.

    This gate is represented by the matrix:
    sqrt(1/2) * [[ 1, -i ],[ -i, 1 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the X2P gate.

        Args:
            label (str | None, optional): An optional label for the X2P gate. Defaults to None.
        """
        super().__init__('X2P', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the X2P gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the X2P gate.
        """
        return sqrt2_inv * np.array([[1, -1j], [-1j, 1]], dtype=dtype)


class X2M(Gate):
    """
    Implements the X2M gate, which applies a rotation around the x-axis of
    the Bloch sphere by -pi/2.

    This gate is represented by the matrix:
    sqrt(1/2) * [[ 1, i ], [ i, 1 ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the X2M gate.

        Args:
            label (str | None, optional): An optional label for the X2M gate. Defaults to None.
        """
        super().__init__('X2M', 1, [], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
         The numpy matrix of the X2M gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the X2M gate.
        """
        return sqrt2_inv * np.array([[1, 1j], [1j, 1]], dtype=dtype)
