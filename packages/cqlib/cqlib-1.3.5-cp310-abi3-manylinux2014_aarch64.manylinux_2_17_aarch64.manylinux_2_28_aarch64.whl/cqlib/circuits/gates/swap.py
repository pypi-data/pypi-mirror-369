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

"""Swap gate."""
from typing import Optional, Sequence
import numpy as np

from cqlib.circuits.gates.gate import Gate


class SWAP(Gate):
    """
     The Swap gate.

    The SWAP gate exchanges the states of two qubits. It is represented by the following matrix:
    [[ 1, 0, 0, 0 ],
    [ 0, 0, 1, 0 ],
    [ 0, 1, 0, 0 ],
    [ 0, 0, 0, 1 ]]
    """
    is_supported_by_qcis = False

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the Swap gate.

        Args:
            label (str | None, optional): An optional label for the Swap gate. Defaults to None.
        """
        super().__init__('SWAP', 2, [], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the Swap gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 4x4 matrix with complex entries representing the Swap gate.
        """
        return np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=dtype)

    def to_qcis(self, qubits: Sequence) -> list:
        """
        Convert the SWAP gate to a sequence of QCIS instructions.

        Args:
            qubits (list | tuple): The list or tuple of qubits the gate acts on.
                                    It requires exactly two qubits.

        Returns:
            list: A list of InstructionData objects representing the SWAP gate in QCIS.

        Raises:
            ValueError: If the number of qubits is not exactly two.
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.circuits.gates.z import CZ
        from cqlib.circuits.gates.y import Y2P, Y2M
        from cqlib.circuits.qubit import Qubit
        from cqlib.circuits.instruction_data import InstructionData

        if len(qubits) != 2:
            raise ValueError("Swap gate requires exactly two qubits.")
        for index, qubit in enumerate(qubits):
            if isinstance(qubit, int):
                qubits[index] = Qubit(qubit)
        q0 = qubits[0]
        q1 = qubits[1]
        return [
            # First CNOT
            InstructionData(Y2M(), [q1]),
            InstructionData(CZ(), [q0, q1]),
            InstructionData(Y2P(), [q1]),

            # Second CNOT
            InstructionData(Y2M(), [q0]),
            InstructionData(CZ(), [q1, q0]),
            InstructionData(Y2P(), [q0]),

            # Third CNOT
            InstructionData(Y2M(), [q1]),
            InstructionData(CZ(), [q0, q1]),
            InstructionData(Y2P(), [q1]),
        ]
