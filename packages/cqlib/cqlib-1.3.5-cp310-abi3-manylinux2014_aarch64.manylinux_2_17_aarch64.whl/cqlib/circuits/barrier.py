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
This module provides the definition of the Barrier class, a part of the
quantum circuit handling system within the cqlib framework. The Barrier
class is used to create synchronization points in quantum circuits.

A barrier in quantum computing is crucial for preventing the quantum compiler
from making certain optimizations that could change the intended execution
order of operations. This is particularly important in scenarios where
the sequence of quantum gates is critical for the algorithm's correctness.

Classes:
    Barrier: Implements a synchronization barrier across multiple qubits
        within a quantum circuit.

Usage:
    The Barrier class is typically used during the assembly of a quantum
    circuit where gate operations need strict adherence to their defined
    sequence. It ensures that all operations before the barrier are completed
    before any operations following the barrier begin execution.
"""
from typing import Optional
from cqlib.circuits.instruction import Instruction


# pylint: disable=R0903
class Barrier(Instruction):
    """
    Represents a quantum barrier that prevents gate reordering by the compiler.

    A barrier is used in quantum circuits to ensure that certain optimizations,
    such as gate reordering, do not alter the intended execution order across
    the specified qubits. This is crucial for maintaining the correct quantum state
    transformations when sequence-dependent gate operations are critical.
    """

    def __init__(self, num_qubits: int, label: Optional[str] = None):
        """
        Initializes a new instance of the Barrier class.

        Args:
            num_qubits (int): The number of qubits the barrier spans. This defines
                the scope of the barrier's effect, preventing any reordering of gates
                that involve these qubits.
            label (str | None, optional): An optional label for the barrier which can be
                used for identification or annotation purposes.

        Note:
            The barrier does not represent a physical quantum operation
            but serves as a control tool within quantum circuits.
        """
        super().__init__("B", num_qubits, [], label=label)
