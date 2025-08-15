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

"""Defines the Rx (rotation around the X-axis) and CRx (Controlled-RX) gate."""
from __future__ import annotations
from typing import Optional, Union, Sequence
import numpy as np

from cqlib.circuits.parameter import Parameter
from cqlib.circuits.gates.gate import Gate, ControlledGate


class RX(Gate):
    """
    Rx gate applies a rotation around the x-axis of the Bloch sphere by a specified angle.

    This gate is represented by the matrix:
    [[ cos(theta/2), -i*sin(theta/2) ],
    [ -i*sin(theta/2), cos(theta/2) ]]
    """

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the Rx gate

        Args:
            theta (float | Parameter): The rotation angle in radians around the X-axis.
            label (str | None, optional): An optional label for the Rx gate. Defaults to None.
        """
        super().__init__('RX', 1, [theta], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the Rx gate

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Rx gate.
        """
        cos = np.cos(self.params[0] / 2)
        sin = np.sin(self.params[0] / 2)

        return np.array([[cos, sin * -1j], [sin * -1j, cos]], dtype=dtype)


class CRX(ControlledGate):
    """
    Controlled-RX (CRX) gate, which is a two-qubit quantum gate.

    This gate applies a controlled rotation around the x-axis on the target qubit
    depending on the state of the control qubit. It is represented by the matrix:
    [[ 1, 0, 0, 0 ],
    [ 0, 1, 0, 0 ],
    [ 0, 0, cos(theta/2), -i*sin(theta/2) ],
    [ 0, 0, -i*sin(theta/2), cos(theta/2) ]]
    """
    is_supported_by_qcis = False

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the CRX gate.

        Args:
            theta (float | Parameter): The rotation angle in radians around the X-axis.
            label (str | None, optional): An optional label for the CRX gate. Defaults to None.
        """
        super().__init__(
            'CRX',
            2,
            control_index=[0],
            base_gate=RX(theta),
            params=[theta],
            label=label
        )

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the CRX gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 4x4 matrix with complex entries representing the CRX gate.
        """
        # pylint: disable=R0801
        sin = np.sin(self.params[0] / 2)
        cos = np.cos(self.params[0] / 2)

        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, cos, sin * -1j],
            [0, 0, sin * -1j, cos]
        ], dtype=dtype)

    # pylint: disable=R0801
    def to_qcis(self, qubits: Sequence) -> list:
        """
        Convert the CRX gate to a sequence of QCIS instructions.

        Args:
            qubits (list | tuple): The list or tuple of qubits the gate acts on.
                It requires exactly two qubits.

        Returns:
            list: A list of InstructionData objects representing the CRX gate in QCIS.

        Raises:
            ValueError: If the number of qubits is not exactly two.
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.circuits.gates.y import Y2M, Y2P
        from cqlib.circuits.gates.z import CZ
        from cqlib.circuits.gates.rz import RZ
        from cqlib.circuits.instruction_data import InstructionData

        control_qubit, target_qubit = self._parse_qubits(qubits)
        return [
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(self.params[0] / 2), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
            InstructionData(CZ(), [control_qubit, target_qubit]),
            InstructionData(Y2M(), [target_qubit]),
            InstructionData(RZ(-self.params[0] / 2), [target_qubit]),
            InstructionData(Y2P(), [target_qubit]),
            InstructionData(CZ(), [control_qubit, target_qubit]),
        ]
