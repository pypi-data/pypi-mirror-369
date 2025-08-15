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
XY gate and its variants XY2P and XY2M, which perform rotations around
the x-axis and y-axis by specific angles.

Classes:
    XY: Performs a composite rotation around the Z and Y axes,
    described by a specific sequence.
    XY2P: Rotates around the X-axis and Y-axis by pi/2.
    XY2M: Rotates around the X-axis and Y-axis by -pi/2.
"""
from typing import Union, Optional
import numpy as np

from cqlib.circuits.gates.gate import Gate
from cqlib.circuits.parameter import Parameter
from cqlib.circuits.utils import sqrt2_inv


class XY(Gate):
    """
    Implements the XY gate, a composite quantum gate that performs a specific series
     of rotations around the Z and Y axes.

    The XY gate is constructed from the following sequence of operations:
    1. Rz(pi/2 - theta): Rotation around the Z-axis by (pi/2 - theta) radians.
    2. Y: Pauli Y gate that rotates the qubit around the Y-axis by pi radians.
    3. Rz(theta - pi/2): Rotation around the Z-axis by (theta - pi/2) radians.
    """

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the XY gate

        Args:
            theta (float | Parameter): The rotation angle in radians around the XY-axis.
            label (str | None, optional): An optional label for the XY gate. Defaults to None.
        """
        super().__init__('XY', 1, [theta], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the XY gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the XY gate.
        """
        return -1j * np.array([[0, np.exp(self.params[0] * -1j)],
                               [np.exp(self.params[0] * 1j), 0]], dtype=dtype)


class XY2P(Gate):
    """
    XY2P gate performs a rotation around the X-axis by pi/2, modulated by a
     phase theta around the Y-axis.
    """

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the XY2P gate.

        Args:
            theta (float | Parameter): The rotation angle in radians around the XY-plane.
            label (str | None, optional): An optional label for the XY2P gate.
                Defaults to None.
        """
        super().__init__('XY2P', 1, [theta], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the XY2P gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the XY2P gate.
        """
        return sqrt2_inv * np.array([[1, -1j * np.exp(self.params[0] * -1j)],
                                     [-1j * np.exp(self.params[0] * 1j), 1]], dtype=dtype)


class XY2M(Gate):
    """
    XY2M gate performs a rotation around the X-axis by -pi/2,
    modulated by a phase theta around the Y-axis.
    """

    def __init__(self, theta: Union[float, Parameter], label: Optional[str] = None):
        """
        Initialize the XY2M gate.

        Args:
            theta (float | Parameter): The rotation angle in radians around the XY-plane.
            label (str | None, optional): An optional label for the XY2M gate. Defaults to None.
        """
        super().__init__('XY2M', 1, [theta], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        The numpy matrix of the XY2M gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the XY2M gate.
        """
        return sqrt2_inv * np.array([[1, 1j * np.exp(self.params[0] * -1j)],
                                     [1j * np.exp(self.params[0] * 1j), 1]], dtype=dtype)
