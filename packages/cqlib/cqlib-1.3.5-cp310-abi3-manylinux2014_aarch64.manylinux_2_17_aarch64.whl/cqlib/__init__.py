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

"""cqlib"""

from cqlib.circuits import Circuit, Barrier, Qubit, Measure, Parameter, Instruction, \
    InstructionData, gates
from cqlib.circuits import dag_to_circuit, circuit_to_dag

from cqlib.quantum_platform import BasePlatform, TianYanPlatform, GuoDunPlatform, QuantumLanguage
