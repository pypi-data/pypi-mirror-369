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

"""Quantum Gate"""
from typing import List, Union, Optional
from cqlib.circuits.qubit import Qubit
from cqlib.circuits.instruction import Instruction
from cqlib.circuits.parameter import Parameter


class Gate(Instruction):
    """
    Quantum Gate

    This class represents a general quantum gate. It is a subclass of the Instruction class.
    """

    def __init__(
            self,
            name: str,
            num_qubits: int,
            params: List[Union[Parameter, float, complex]],
            label: Optional[str] = None
    ):
        """
        Create gate object.

         Args:
            name (str): The name of the gate.
            num_qubits (int): The number of qubits the gate acts on.
            params (list[Parameter | float | complex]): A list of parameters for the gate.
            label (str | None, optional): An optional label for the gate. Defaults to None.

         """
        super().__init__(name, num_qubits, params, label)

    def __array__(self, dtype=None):
        """
        Convert the gate to a numpy array representation.

        This method is not implemented and will raise an error if called.

        Args:
            dtype: The desired data type for the array (optional).

        Raises:
            NotImplementedError: This method is not implemented yet.
        """
        raise NotImplementedError("Not implemented yet")


class ControlledGate(Gate):
    """
    A quantum gate with one or more control qubits.

    This class represents a quantum gate that has control qubits in addition to target qubits.
    """

    # pylint: disable=useless-parent-delegation,too-many-arguments,too-many-positional-arguments
    def __init__(
            self,
            name: str,
            num_qubits: int,
            control_index: list[int],
            base_gate: Gate,
            params: List[Union[Parameter, float, complex]],
            label: Optional[str] = None
    ):
        """
        Create a controlled gate object.

        Args:
            name (str): The name of the controlled gate.
            num_qubits (int): The number of qubits the gate acts on.
            control_index (list[int]): A list of indices specifying the control qubits
                for the gate. Each index represents a qubit within the range of
                `[0, num_qubits - 1]` that acts as a control for the gate operation.
            base_gate (Gate): Gate object to be controlled.
            params (list[Parameter | float | complex]): A list of parameters for the gate.
            label (str | None, optional): An optional label for the gate. Defaults to None.
        """
        super().__init__(name, num_qubits, params, label)
        self.control_index = control_index
        self.base_gate = base_gate
        assert all(map(lambda s: s < self.num_qubits, self.control_index))

    def __array__(self, dtype=None):
        """
        Convert the gate to a numpy array representation.

        This method is not implemented and will raise an error if called.

        Args:
            dtype: The desired data type for the array (optional).

        Raises:
            NotImplementedError: This method is not implemented yet.
        """
        raise NotImplementedError("Not implemented yet")

    def _parse_qubits(self, qubits):
        if len(qubits) != self.num_qubits:
            raise ValueError(f"{self.__class__.__name__} gate requires"
                             f" exactly {self.num_qubits} qubits.")

        for index, qubit in enumerate(qubits):
            if isinstance(qubit, int):
                qubits[index] = Qubit(qubit)

        return qubits
