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
This module defines the U quantum gates commonly used in quantum computing.
These gates represent single-qubit rotations around the Bloch sphere and are parameterized
by angles that control the rotation and phase.

Definitions:
    - U(θ, ϕ, λ): General single-qubit rotation gate.
    - U3(θ, ϕ, λ) = U(θ, ϕ, λ)
    - U2(ϕ, λ) = U(π/2, ϕ, λ)
    - U1(λ) = P(λ) = U(0, 0, λ)
"""

import math
from typing import Optional, Sequence

import numpy as np

from cqlib.circuits.instruction_data import InstructionData
from cqlib.circuits.qubit import Qubit
from cqlib.circuits.gates.gate import Gate
from cqlib.circuits.parameter import Parameter


class U(Gate):
    """
    U gate in quantum computing

    It is represented by the matrix:
    U(theta,phi,lam)=
            [ [ cos(theta/2),                 -exp(i * lam) * sin(theta/2)],
              [ exp(i * phi) * sin(theta/2), exp(i * (phi+lam)) * cos(theta/2)]]

    """
    is_supported_by_qcis = False

    def __init__(
            self,
            theta: float | Parameter,
            phi: float | Parameter,
            lam: float | Parameter,
            label: Optional[str] = None
    ):
        """
        Initializes the U gate with parameters theta, phi, and lam.

        Args:
            theta (float | Parameter): Rotation angle theta.
            phi (float | Parameter): Phase angle phi.
            lam (float | Parameter): Phase angle lambda.
            label (str | None, optional): An optional label for the X gate. Defaults to None.
        """
        super().__init__('U', 1, [theta, phi, lam], label=label)

    def __array__(self, dtype: np.dtype = np.complex128):
        """
        Returns the matrix representation of the U gate.

        Args:
            dtype (optional): The data type of the matrix elements. Default is np.complex128.

        Returns:
            numpy.ndarray: A 2x2 matrix with complex entries representing the U gate.
        """
        theta, phi, lam = (float(param) for param in self.params)
        cos = math.cos(theta / 2)
        sin = math.sin(theta / 2)
        return np.array(
            [
                [cos, -np.exp(1j * lam) * sin],
                [np.exp(1j * phi) * sin, np.exp(1j * (phi + lam)) * cos],
            ],
            dtype=dtype or complex,
        )

    def to_qcis(self, qubits: Sequence[Qubit]) -> list[InstructionData]:
        """
        Convert the U gate to a sequence of QCIS instructions.
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.circuits.gates.rz import RZ
        from cqlib.circuits.gates.y import Y2P, Y2M

        qubit = qubits[0]
        theta, phi, lam = (float(param) for param in self.params)
        return [
            InstructionData(RZ(lam + math.pi / 2), [qubit]),
            InstructionData(Y2P(), [qubit]),
            InstructionData(RZ(theta), [qubit]),
            InstructionData(Y2M(), [qubit]),
            InstructionData(RZ(phi - math.pi / 2), [qubit]),
        ]
