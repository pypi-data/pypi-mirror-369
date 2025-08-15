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

"""Defines the Rz (rotation around the Z-axis) and CRz (Controlled-Rz) gate."""
from math import pi
from typing import Union, Optional, Sequence
import numpy as np

from cqlib.circuits.parameter import Parameter
from cqlib.circuits.gates.gate import Gate, ControlledGate


class RZ(Gate):
    """
    Rz gate applies a rotation around the z-axis of the Bloch sphere by a specified angle.

    This gate is represented by the matrix:
    [[ exp(-i*theta/2), 0 ],
    [ 0, exp(i*theta/2) ]]
    """

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the Rz gate

        Args:
            theta (float | Parameter): The rotation angle in radians around the Z-axis.
            label (str | None, optional): An optional label for the Rz gate. Defaults to None.
        """
        super().__init__('RZ', 1, [theta], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the Rz gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Rz gate.
        """
        return np.array([
            [np.exp(-1j * self.params[0] / 2), 0],
            [0, np.exp(1j * self.params[0] / 2)]
        ], dtype=dtype)


class CRZ(ControlledGate):
    """
    Controlled-Rz (CRZ) gate, which is a two-qubit quantum gate.

    This gate applies a controlled rotation around the z-axis on the target qubit
    depending on the state of the control qubit. It is represented by the matrix:
    [[ 1, 0, 0, 0 ],
    [ 0, 1, 0, 0 ],
    [ 0, 0, exp(-i*theta/2), 0 ],
    [ 0, 0, 0, exp(i*theta/2) ]]
    """
    is_supported_by_qcis = False

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the CRZ gate.

        Args:
            theta (float | Parameter): The rotation angle in radians around the Z-axis.
            label (str | None, optional): An optional label for the CRZ gate. Defaults to None.
        """
        super().__init__(
            'CRZ',
            2,
            control_index=[0],
            base_gate=RZ(theta),
            params=[theta],
            label=label
        )

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the CRZ gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 4x4 matrix with complex entries representing the CRZ gate.
        """
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.exp(-1j * self.params[0] / 2), 0],
            [0, 0, 0, np.exp(1j * self.params[0] / 2)]
        ], dtype=dtype)

    def to_qcis(self, qubits: Sequence) -> list:
        """
        Convert the CRZ gate to a sequence of QCIS instructions.

        Args:
            qubits (list | tuple): The list or tuple of qubits the gate acts on.
                It requires exactly two qubits.

        Returns:
            list: A list of InstructionData objects representing the CRZ gate in QCIS.

        Raises:
            ValueError: If the number of qubits is not exactly two.
        """
        # pylint: disable=import-outside-toplevel, cyclic-import
        from cqlib.circuits.gates.z import CZ
        from cqlib.circuits.gates.y import Y2M, Y2P
        from cqlib.circuits.instruction_data import InstructionData

        control_qubit, target_qubit = self._parse_qubits(qubits)
        return [
            InstructionData(RZ(self.params[0] / 2 + pi), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
            InstructionData(CZ(), [control_qubit, target_qubit]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(-self.params[0] / 2), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
            InstructionData(CZ(), [control_qubit, target_qubit]),
            InstructionData(RZ(pi), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
        ]
