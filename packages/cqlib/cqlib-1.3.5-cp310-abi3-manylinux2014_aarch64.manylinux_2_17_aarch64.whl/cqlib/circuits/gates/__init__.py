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
Quantum gates
"""

from .h import H
from .i import I
from .rx import RX, CRX
from .rxy import RXY
from .ry import RY, CRY
from .rz import RZ, CRZ
from .s import S, SD
from .swap import SWAP
from .t import T, TD
from .u import U
from .x import X, CX, CNOT, CCX, CCNOT, X2P, X2M
from .xy import XY, XY2M, XY2P
from .y import Y, Y2M, Y2P, CY
from .z import Z, CZ

__all__ = (
    'H',
    'I',
    'RX', 'CRX',
    'RXY',
    'RY', 'CRY',
    'RZ', 'CRZ',
    'S', 'SD',
    'SWAP',
    'T', 'TD',
    'U',
    'X', 'CX', 'CCX', 'CNOT', 'CCNOT', 'X2P', 'X2M',
    'XY', 'XY2P', 'XY2M',
    'Y', 'Y2M', 'Y2P', 'CY',
    'Z', 'CZ'
)
