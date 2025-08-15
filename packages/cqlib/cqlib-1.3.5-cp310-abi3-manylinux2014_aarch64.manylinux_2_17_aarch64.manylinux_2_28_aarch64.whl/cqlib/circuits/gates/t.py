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

"""The T, TD(T dagger) gates."""
from typing import Optional
import numpy as np

from cqlib.circuits.gates.gate import Gate


class T(Gate):
    """
    The T (Phase) gate, which applies a phase of pi/4.

    This gate is represented by the matrix:
    [[ 1, 0 ],
    [ 0, exp(i*pi/4) ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the T gate.

        Args:
            label (str | None, optional): An optional label for the T gate. Defaults to None.
        """
        super().__init__('T', 1, [], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the T gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the T gate.
        """
        return np.array([[1, 0], [0, np.exp(np.pi / 4 * 1j)]], dtype=dtype)


class TD(Gate):
    """
    Implements the TD gate (T dagger), which applies a phase of -pi/4.

    This gate is represented by the matrix:
    [[ 1, 0 ],
    [ 0, exp(-i*pi/4) ]]
    """

    def __init__(self, label: Optional[str] = None):
        """
        Initialize the TD gate.

        Args:
            label (str | None, optional): An optional label for the TD gate. Defaults to None.
        """
        super().__init__('TD', 1, [], label=label)

    def __array__(self, dtype=np.complex128):
        """
        The numpy matrix of the TD gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the TD gate.
        """
        return np.array([[1, 0], [0, np.exp(np.pi / 4 * -1j)]], dtype=dtype)
