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

"""Generic quantum instruction data."""

from typing import NamedTuple, Sequence

from cqlib.circuits.bit import Bit
from cqlib.circuits.instruction import Instruction


class InstructionData(NamedTuple):
    """
    InstructionData represents a quantum instruction, including the type of
    instruction and the qubits it affects.
    """
    instruction: Instruction
    qubits: Sequence[Bit]

    def __repr__(self):
        s = [self.instruction.name, " ".join(map(str, self.qubits))]
        if self.instruction.params:
            s.append(" ".join(map(str, self.instruction.params)))
        return ' '.join(s)

    def __hash__(self):
        return hash((self.instruction, tuple(self.qubits)))
