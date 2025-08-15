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

"""The S, SD(S dagger) gates."""
from typing import Optional
import numpy as np

from cqlib.circuits.gates.gate import Gate


class S(Gate):
    """
    The S (Phase) gate, which applies a phase of pi/2.

    This gate is represented by the matrix:
    [[ 1, 0 ],
    [ 0, i ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the S gate.

        Args:
            label (str | None, optional): An optional label for the S gate. Defaults to None.
        """
        super().__init__('S', 1, [], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the S gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the S gate.
        """
        return np.array([[1, 0], [0, 1j]], dtype=dtype)


class SD(Gate):
    """
    Implements the SD gate (S dagger), which applies a phase of -pi/2.

    This gate is represented by the matrix:
    [[ 1, 0 ],
    [ 0, -i ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the SD gate.

        Args:
            label (str | None, optional): An optional label for the SD gate. Defaults to None.
        """
        super().__init__('SD', 1, [], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the SD gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the SD gate.
        """
        return np.array([[1, 0], [0, -1j]], dtype=dtype)
