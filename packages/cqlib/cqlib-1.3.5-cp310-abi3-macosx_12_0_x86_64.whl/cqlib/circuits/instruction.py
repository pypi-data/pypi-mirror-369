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

"""Generic quantum instruction."""

from __future__ import annotations

from copy import copy
from typing import List, Optional, Union, Sequence

from .parameter import Parameter


class Instruction:
    """Generic quantum instruction."""

    is_supported_by_qcis = True

    def __init__(
            self,
            name: str,
            num_qubits: int,
            params: Optional[List[Union[Parameter, float, complex]]] = None,
            label: Optional[str] = None
    ):
        """
        Initializes a new quantum instruction.

        Args:
            name: The name of the instruction.
            num_qubits: The number of qubits involved in the instruction.
                        Must be non-negative.
            params: A list of parameters for the instruction, which can
                    include fixed values or parameters.
            label: An optional label for identifying the instruction.
        """
        if num_qubits < 0:
            raise ValueError(f"Invalid number of qubits: {num_qubits}. "
                             f"Number must be non-negative.")
        self.name = name
        self.num_qubits = num_qubits
        self.params = params
        self.label = label

    def __str__(self) -> str:
        params = self._format_params()
        return f'{self.name}({params})' if params else self.name

    def __repr__(self) -> str:
        return self.__str__()

    def copy(self) -> "Instruction":
        """
        Copy the Instruction.
        """
        new_instance = type(self).__new__(type(self))
        new_instance.__dict__.update(self.__dict__)
        if self.params:
            new_instance.params = [p.copy() if isinstance(p, Parameter)
                                   else copy(p) for p in self.params]
        return new_instance

    def _format_params(self) -> str:
        """Formats the parameter list for string representation."""
        return ",".join(str(p) for p in self.params)

    # pylint: disable=unused-argument
    def to_qcis(self, qubits: Sequence):
        """
        Prevents usage of this method for instructions that QCIS supports.

        Do not call this method if QCIS supports the instruction. Instead,
        override this method to provide the necessary implementation for
        instructions that QCIS does not support.

        Args:
            qubits (list | tuple): Qubits affected by this instruction.

        Raises:
            RuntimeError: If called for an instruction that QCIS supports.
            NotImplementedError: If called for an instruction that QCIS does
            not support, and you have not provided an implementation.
        """
        if self.is_supported_by_qcis:
            raise RuntimeError(f"Instruction {self.name} is supported by QCIS and"
                               f" should not use the to_qcis method.")
        raise NotImplementedError(f"Instruction {self.name} not supported by QCIS.")
