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
Identity Gate (I) represents no operation on the qubit for a specified
time period t (in nanoseconds, ns).
The time t is given in integer units of 0.5 ns.
For example, when t=1, the duration is 0.5 ns.
"""
from typing import Optional
import numpy as np

from cqlib.circuits.gates.gate import Gate


class I(Gate):
    """
    Identity gate (I gate), represents no operation on a qubit over a time period.

    The Identity gate leaves the state of the qubit unchanged. It is useful for timing
    and synchronization purposes in quantum circuits.
    """

    def __init__(self, t: int, label: Optional[str] = None):
        """
        Initialize the "I" gate

        Args:
            t (int): The duration the gate acts, in integer units of 0.5 ns.
            label (str | None, optional): An optional label for the I gate. Defaults to None.
        """
        super().__init__('I', 1, [t], label=label)

    def __array__(self, dtype=np.complex128):
        """
        Returns the numpy matrix representation of I gate as a unit matrix.

        This method returns the 2x2 identity matrix, representing the Identity gate.

        Args:
            dtype (optional): The desired data type for the numpy array. Defaults to np.complex128.

        Returns:
            np.ndarray: 2x2 identity matrix.
        """
        return np.eye(2, dtype=dtype)
