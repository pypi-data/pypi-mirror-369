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

"""Defines the Rxy (rotation around the X-axis and Y-axis) gate."""
from typing import Union, Optional
import numpy as np

from cqlib.circuits.parameter import Parameter
from cqlib.circuits.gates.gate import Gate


class RXY(Gate):
    """
    Rxy gate.

    This gate represents a rotation around both the X-axis by an angle phi
    and the Y-axis by an angle theta. It combines rotations around two axes,
    making it a versatile tool for manipulating qubit states.
    """

    def __init__(
            self,
            phi: Union[float, Parameter], theta: Union[float, Parameter],
            label: Optional[str] = None
    ):
        """
        Initialize the Rxy gate.

        The Rxy gate represents a rotation around the X-axis by an angle phi
         and around the Y-axis by an angle theta.

         Args:
            phi (float | Parameter): The rotation angle in radians around the X-axis.
            theta (float | Parameter): The rotation angle in radians around the Y-axis.
            label (str | None, optional): An optional label for the Rxy gate. Defaults to None.
        """
        super().__init__('RXY', 1, [phi, theta], label=label)

    def __array__(self, dtype=np.complex128):
        """
        Return the numpy matrix representation of the Rxy gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the Rxy gate.
        """
        phi = self.params[0]
        theta = self.params[1]

        return np.array([
            [np.cos(theta / 2), -1j * np.exp(-1j * phi) * np.sin(theta / 2)],
            [-1j * np.exp(1j * phi) * np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=dtype)
