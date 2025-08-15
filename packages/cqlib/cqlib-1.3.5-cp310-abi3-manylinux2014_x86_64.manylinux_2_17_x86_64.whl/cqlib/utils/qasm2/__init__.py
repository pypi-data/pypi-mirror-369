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
cqlib.utils.qasm2

This module provides functionality to serialize and deserialize quantum circuits
to and from the OpenQASM 2.0 format. It serves as the interface for converting
`Circuit` objects within the `cqlib` library to OpenQASM strings or files, and
for loading OpenQASM representations back into `Circuit` objects.
"""

from .load import loads, load
from .dump import dumps, dump

__all__ = ['loads', 'load', 'dump', 'dumps']
