# This code is part of cqlib.
#
# (C) Copyright China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Quantum circuit"""

# pylint: disable=too-many-lines

from __future__ import annotations

import re
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal
from numbers import Number
from typing import Union, Sequence, Optional

import numpy as np
import sympy

from cqlib.circuits import gates
from cqlib.circuits.barrier import Barrier
from cqlib.circuits.instruction import Instruction
from cqlib.circuits.instruction_data import InstructionData
from cqlib.circuits.measure import Measure
from cqlib.circuits.parameter import Parameter
from cqlib.circuits.qubit import Qubit
from cqlib.utils.typing import ArrayLike
from cqlib.exceptions import VisualizationError

# Type Alias Definition
Qubits = Union[Qubit, int, Sequence[Union[Qubit, int]]]
IntQubit = Union[Qubit, int]


# pylint: disable=too-many-public-methods
class Circuit:
    """Represents a quantum circuit that can perform various quantum operations."""

    def __init__(self, qubits: Qubits,
                 parameters: Optional[Sequence[Union[Parameter, str]]] = None) -> None:
        """
        Initializes a quantum circuit.

        Args:
            qubits (Qubits): Number of qubits or list of qubits.:
            parameters (list[Parameter | str], optional): List of parameters or parameter names.
        """
        self._qubits: dict[str, Qubit] = self._initialize_qubits(qubits)
        self._parameters: dict[Parameter, Optional[float]] = self._initialize_parameters(parameters)
        self._circuit_data: list[InstructionData] = []

    @staticmethod
    def _initialize_parameters(
            parameters: Sequence[Union[Parameter, str]]
    ) -> dict[Parameter, Optional[float]]:
        """Helper function to initialize parameters."""
        params = {}
        if parameters is None:
            return {}
        for parameter in parameters:
            if isinstance(parameter, str):
                parameter = Parameter(parameter)
            elif not isinstance(parameter, Parameter):
                raise TypeError("Parameters must be of type Parameter or str.")
            if parameter in params:
                raise ValueError(f"Duplicate parameter detected: {parameter}")
            params[parameter] = None
        return params

    @staticmethod
    def _initialize_qubits(qubits: Qubits) -> dict[str, Qubit]:
        """
        Helper function to initialize qubits.

        Args:
            qubits (Qubits): Input qubits specification.

        Returns:
            dict[int, Qubit]: Dictionary of Qubit objects.
        """
        if isinstance(qubits, int):
            if qubits < 0:
                raise ValueError("Number of qubits must be non-negative.")
            return {str(Qubit(i)): Qubit(i) for i in range(qubits)}
        if isinstance(qubits, Qubit):
            return {str(qubits): qubits}
        if isinstance(qubits, (list, tuple)):
            qs = {}
            for qubit in qubits:
                if isinstance(qubit, int):
                    qubit = Qubit(qubit)
                elif not isinstance(qubit, Qubit):
                    raise TypeError("Qubit must be an int or QuBit instance.")
                if qubit.index in qs:
                    raise ValueError(f"Duplicate qubit detected: {qubit}")
                qs[str(qubit)] = qubit
            return qs
        raise ValueError("Invalid qubits input. Expected int, QuBit, or list/tuple of these.")

    @property
    def qubits(self) -> list[Qubit]:
        """circuit qubits"""
        return list(self._qubits.values())

    @property
    def num_qubits(self) -> int:
        """Return number of qubits."""
        return len(self._qubits)

    @property
    def circuit_data(self):
        """Circuit data"""
        return self._circuit_data

    def qubits_path(self) -> dict[Qubit, list[InstructionData]]:
        """
        Constructs a path of operations for each qubit.
        """
        path = defaultdict(list)
        max_depths = defaultdict(int)
        for op in self._circuit_data:
            instruction = op.instruction
            qubits = op.qubits
            if instruction.num_qubits != len(qubits):
                raise ValueError("Instruction qubit count does not match provided qubits.")
            current_max_depth = max(max_depths[qubit] for qubit in qubits)
            for qubit in qubits:
                ops = [None] * (current_max_depth - max_depths[qubit]) + [op]
                path[qubit].extend(ops)
                max_depths[qubit] = current_max_depth + 1
        return path

    def depth(self) -> int:
        """Max length of critical path"""
        path = self.qubits_path()
        return max(len(ops) for _, ops in path.items())

    def add_qubit(self, qubit: IntQubit):
        """
        Adds a qubit to the circuit, ensuring it does not already exist.

        Args:
            qubit (IntQubit): The qubit to add, specified as an integer index or a Qubit object.
        """
        if isinstance(qubit, int):
            qubit = Qubit(qubit)
        elif not isinstance(qubit, Qubit):
            raise TypeError("Qubit must be an int or QuBit instance.")
        if str(qubit) in self._qubits:
            raise ValueError("Qubit already exists in the circuit.")
        self._qubits[str(qubit)] = qubit

    @property
    def parameters(self) -> list[Parameter]:
        """
        Retrieves a list of all parameters currently in the quantum circuit.

        Returns:
            list[Parameter]: A list containing the parameters used in the circuit.
        """
        return list(self._parameters.keys())

    @property
    def parameters_value(self) -> dict[Parameter, Union[float, int]]:
        """
        Retrieves a list of all parameters currently in the quantum circuit.

        Returns:
            dict[Parameter, Union[float, int]]: parameters
        """
        return self._parameters

    def add_parameter(self, parameter: Union[Parameter, str]):
        """
        Adds a new parameter to the quantum circuit.
        If the parameter already exists, it raises an error.

        Args:
            parameter (Parameter | str): The parameter to add, can be an instance of
                Parameter or a string name. If a string is provided, a new Parameter
                instance will be created from it.
        """
        if isinstance(parameter, str):
            parameter = Parameter(parameter)
        elif not isinstance(parameter, Parameter):
            raise TypeError("Parameters must be of type Parameter or str.")
        if parameter in self._parameters:
            raise ValueError("Parameter already exists in the circuit.")
        self._parameters[parameter] = None

    @property
    def instruction_sequence(self) -> list[InstructionData]:
        """
        Accesses the list of all instruction data objects stored in the circuit.

        Returns:
            list[InstructionData]: The sequence of instructions added to the circuit,
                each represented by an InstructionData object.
        """
        return self._circuit_data

    def insert(self, instruction: Instruction, qubits: Qubits, index: int = None):
        """
        Insert an instruction into the circuit at a specified index.

        Args:
            instruction (Instruction): The instruction to be inserted.
            qubits (Qubits): The qubit(s) to which the instruction is applied.
            index (int, optional): The index at which to insert the instruction.
                Defaults to None, which appends at the end.
        """
        instruction, qubits = self._prepare_instruction(instruction, qubits)
        if index is None:
            index = len(self._circuit_data)
        elif not isinstance(index, int):
            raise TypeError("Index must be an integer or None.")
        elif index < 0 or index > len(self._circuit_data):
            raise ValueError(f"Index {index} out of bounds for instructions list of length "
                             f"{len(self._circuit_data)}.")

        self._circuit_data.insert(
            index,
            InstructionData(instruction=instruction, qubits=qubits)
        )

    def append(self, instruction: Instruction, qubits: Qubits):
        """
        append instruction to circuit

        Args:
            instruction (Instruction): The instruction to be appended.
            qubits (Qubits): The qubit(s) to which the instruction is applied.
        """
        instruction, qubits = self._prepare_instruction(instruction, qubits)
        self._circuit_data.append(InstructionData(instruction=instruction, qubits=qubits))

    def append_instruction_data(self, instruction_data: InstructionData):
        """
        append instruction_data to circuit

        Args:
            instruction_data (InstructionData): The instruction_data to be appended.
        """
        self._circuit_data.append(instruction_data)

    def _prepare_instruction(self, instruction: Instruction, qubits: Qubits):
        """
        append instruction to circuit

        Args:
            instruction (Instruction): The instruction to be appended.
            qubits (Qubits): The qubit(s) to which the instruction is applied.
        """
        qs = self._normalize_qubits(qubits)
        if instruction.num_qubits != len(qs):
            raise ValueError(f"Instruction requires {instruction.num_qubits} qubits,"
                             f" but {len(qubits)} were given.")
        self._update_instruction_params(instruction)
        return instruction, qs

    def _normalize_qubits(self, qubits: Qubits) -> list[Qubit]:
        """ Normalize and validate qubits input. """
        if not isinstance(qubits, (list, tuple)):
            qubits = [qubits]

        qs = []
        for q in qubits:
            if isinstance(q, int):
                q = Qubit(q)
            if not isinstance(q, Qubit):
                raise TypeError(f"{q} must be an instance of QuBit or an integer.")
            if str(q) not in self._qubits:
                raise ValueError(f"{q} not found in circuit.")
            qs.append(q)
        return qs

    def _update_instruction_params(self, instruction: Instruction):
        """ Validate and set parameters for the instruction. """
        if not instruction.params:
            return
        params = []
        for param in instruction.params:
            if isinstance(param, str):
                param = Parameter(param)
            if isinstance(param, Parameter):
                for p in param.base_params:
                    if p not in self._parameters:
                        raise ValueError(f"Parameter {p} not found in circuit.")
            params.append(param)
        instruction.params = params

    def h(self, qubit: IntQubit):
        """
        Applies the Hadamard gate (H) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the Hadamard gate.
        """
        self.append(gates.H(), [qubit])

    def i(self, qubit: IntQubit, t: int):
        """
        Applies the `I` gate to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the Hadamard gate.
            t (int): The duration the gate acts, in integer units of 0.5 ns.
        """
        self.append(gates.I(t), [qubit])

    def rx(self, qubit: IntQubit, theta: Union[float, Parameter]):
        """
        Applies the RX gate (rotation around the X-axis) to a specified
            qubit with a given angle.

        Args:
            qubit (IntQubit): The qubit to apply the RX gate.
            theta (Union[float, Parameter]): The rotation angle in radians or as
                a symbolic parameter.
        """
        self.append(gates.RX(theta), [qubit])

    def rxy(self, qubit: IntQubit, phi: Union[float, Parameter],
            theta: Union[float, Parameter]):
        """
        Applies the RX gate (rotation around the X-axis) to a specified
            qubit with a given angle.

        Args:
            qubit (IntQubit): The qubit to apply the RX gate.
            phi (Union[float, Parameter]): The rotation angle in radians or
                as a symbolic parameter.
            theta (Union[float, Parameter]): The rotation angle in radians or
                as a symbolic parameter.
        """
        self.append(gates.RXY(phi, theta), [qubit])

    def crx(self, control_qubit: IntQubit, target_qubit: IntQubit,
            theta: Union[float, Parameter]):
        """
        Applies the controlled-RX gate (controlled rotation around the X-axis)
        between two qubits.

        Args:
            control_qubit (IntQubit): The control qubit.
            target_qubit (IntQubit): The target qubit where the rotation is applied.
            theta (Union[float, Parameter]): The rotation angle in radians or as a
                symbolic parameter.
        """
        self.append(gates.CRX(theta), [control_qubit, target_qubit])

    def ry(self, qubit: IntQubit, theta: Union[float, Parameter]):
        """
         Applies the RY gate (rotation around the Y-axis) to a specified qubit
         with a given angle.

         Args:
             qubit (IntQubit): The qubit to apply the RY gate.
             theta (Union[float, Parameter]): The rotation angle in radians or
                as a symbolic parameter.
         """
        self.append(gates.RY(theta), [qubit])

    def cry(self, control_qubit: IntQubit, target_qubit: IntQubit,
            theta: Union[float, Parameter]):
        """
        Applies the controlled-RY gate (controlled rotation around the Y-axis)
        between two qubits.

        Args:
            control_qubit (IntQubit): The control qubit.
            target_qubit (IntQubit): The target qubit where the rotation is applied.
            theta (Union[float, Parameter]): The rotation angle in radians or
                as a symbolic parameter.
        """
        self.append(gates.CRY(theta), [control_qubit, target_qubit])

    def rz(self, qubit: IntQubit, theta: Union[float, Parameter]):
        """
        Applies the RZ gate (rotation around the Z-axis) to a specified qubit
        with a given angle.

        Args:
            qubit (IntQubit): The qubit to apply the RZ gate.
            theta (Union[float, Parameter]): The rotation angle in radians or
                as a symbolic parameter.
        """
        self.append(gates.RZ(theta), [qubit])

    def crz(self, control_qubit: IntQubit, target_qubit: IntQubit, theta: Union[float, Parameter]):
        """
        Applies the controlled-RZ gate (controlled rotation around the Z-axis) between two qubits.

        Args:
            control_qubit (IntQubit): The control qubit.
            target_qubit (IntQubit): The target qubit where the rotation is applied.
            theta (Union[float, Parameter]): The rotation angle in radians or
                as a symbolic parameter.
        """
        self.append(gates.CRZ(theta), [control_qubit, target_qubit])

    def s(self, qubit: IntQubit):
        """
        Applies the S gate (phase gate) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the S gate.
        """
        self.append(gates.S(), [qubit])

    def sd(self, qubit: IntQubit):
        """
        Applies the S-dagger gate (inverse S gate) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the S-dagger gate.
        """
        self.append(gates.SD(), [qubit])

    def swap(self, qubit1: IntQubit, qubit2: IntQubit):
        """
        Applies the SWAP gate to exchange the states of two specified qubits.

        Args:
            qubit1 (IntQubit): The first qubit.
            qubit2 (IntQubit): The second qubit.
        """
        self.append(gates.SWAP(), [qubit1, qubit2])

    def t(self, qubit: IntQubit):
        """
        Applies the T gate (π/8 gate) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the T gate.
        """
        self.append(gates.T(), [qubit])

    def td(self, qubit: IntQubit):
        """
        Applies the TD gate (-π/8 gate) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the T gate.
        """
        self.append(gates.TD(), [qubit])

    def x(self, qubit: IntQubit):
        """
        Applies the X gate (Pauli X, flip gate) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the X gate.
        """
        self.append(gates.X(), [qubit])

    def cx(self, control_qubit: IntQubit, target_qubit: IntQubit):
        """
        Applies the CX gate (controlled-X, CNOT) between a control qubit and a target qubit.

        Args:
            control_qubit (IntQubit): The control qubit.
            target_qubit (IntQubit): The target qubit where the NOT operation is applied
             conditionally.
        """
        self.append(gates.CX(), [control_qubit, target_qubit])

    def ccx(self, control_qubit_1: IntQubit, control_qubit_2: IntQubit, target_qubit: IntQubit):
        """
        Applies the CCX gate (Toffoli gate, controlled-controlled-X) using two control qubits
        and one target qubit.

        Args:
            control_qubit_1 (IntQubit): The first control qubit.
            control_qubit_2 (IntQubit): The second control qubit.
            target_qubit (IntQubit): The target qubit where the X operation is applied
                conditionally.
        """
        self.append(gates.CCX(), [control_qubit_1, control_qubit_2, target_qubit])

    def x2p(self, qubit: IntQubit):
        """
        Applies the X2P gate to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the X2P gate.
        """
        self.append(gates.X2P(), [qubit])

    def x2m(self, qubit: IntQubit):
        """
         Applies the X2M gate to a specified qubit.

         Args:
             qubit (IntQubit): The qubit to apply the X2M gate.
         """
        self.append(gates.X2M(), [qubit])

    def xy(self, qubit: IntQubit, theta: Union[float, Parameter]):
        """
        Applies the XY gate (generalized rotation around an axis in the XY plane)
        to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the XY gate.
            theta (Union[float, Parameter]): The rotation angle around the XY axis.
        """
        self.append(gates.XY(theta), [qubit])

    def xy2p(self, qubit: IntQubit, theta: Union[float, Parameter]):
        """
        Applies the XY2P gate to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the XY2P gate.
            theta (Union[float, Parameter]): The rotation angle for the root operation.
        """
        self.append(gates.XY2P(theta), [qubit])

    def xy2m(self, qubit: IntQubit, theta: Union[float, Parameter]):
        """
        Applies the XY2M gate to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the XY2M gate.
            theta (Union[float, Parameter]): The rotation angle for the root operation.
        """
        self.append(gates.XY2M(theta), [qubit])

    def y(self, qubit: IntQubit):
        """
        Applies the Y gate (Pauli Y) to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the Y gate.
        """
        self.append(gates.Y(), [qubit])

    def cy(self, control_qubit: IntQubit, target_qubit: IntQubit):
        """
        Applies the CY (Controlled-Y) gate to the specified control and target qubits.

        Args:
            control_qubit (IntQubit): The control qubit.
            target_qubit (IntQubit): The target qubit where the CY operation is applied
             conditionally.
        """
        self.append(gates.CY(), [control_qubit, target_qubit])

    def y2p(self, qubit: IntQubit):
        """
        Applies the Y2P gate to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the Y2P gate.
        """
        self.append(gates.Y2P(), [qubit])

    def y2m(self, qubit: IntQubit):
        """
        Applies the Y2M gate to a specified qubit.

        Args:
            qubit (IntQubit): The qubit to apply the Y2M gate.
        """
        self.append(gates.Y2M(), [qubit])

    def z(self, qubit: IntQubit):
        """
       Applies the Z gate (Pauli Z) to a specified qubit.

       Args:
           qubit (IntQubit): The qubit to apply the Z gate.
       """
        self.append(gates.Z(), [qubit])

    def cz(self, control_qubit: IntQubit, target_qubit: IntQubit):
        """
        Applies the CZ gate (controlled-Z) between a control qubit and a target qubit.

        Args:
            control_qubit (IntQubit): The control qubit.
            target_qubit (IntQubit): The target qubit where the Z operation is applied
             conditionally.
        """
        self.append(gates.CZ(), [control_qubit, target_qubit])

    def u(
            self,
            qubit: IntQubit,
            theta: Union[float, Parameter],
            phi: Union[float, Parameter],
            lam: Union[float, Parameter]
    ):
        """
        Applies the U gate to a specified qubit.

        Args:
            qubit (IntQubit): The target qubit to which the U gate is applied.
            theta (float | Parameter): The rotation angle theta (θ) around the Bloch sphere.
            phi (float | Parameter): The phase angle phi (φ) for the first Z-axis rotation.
            lam (float | Parameter): The phase angle lambda (λ) for the final Z-axis rotation.
        """
        self.append(gates.U(theta, phi, lam), [qubit])

    def barrier(self, *qubits: IntQubit):
        """
        Inserts a barrier into the circuit that affects all specified qubits.
        A barrier ensures that no optimizations or rearrangements are done across
        this point in the circuit, maintaining the order of operations.

        Args:
            qubits (IntQubit): The qubits to which the barrier is applied.
        """
        self.append(Barrier(len(qubits)), list(qubits))

    def barrier_all(self):
        """
        Insert barrier instruction for all qubits in the circuit.
        """
        qs = self._qubits.values()
        self.append(Barrier(len(qs)), list(qs))

    def measure(self, qubits: Qubits):
        """
        Measures the specified qubits and collapses their quantum state into classical bits.

        Args:
            qubits (Qubits): The qubits to measure, can be a single qubit or a list of qubits.
        """
        if isinstance(qubits, (Qubit, int)):
            qubits = [qubits]

        for q in qubits:
            self.append(Measure(), [q])

    def measure_all(self):
        """
        Measures all qubits in the circuit that have not yet been measured.
        """
        measured_qubits = set()
        for ins in self._circuit_data:
            if isinstance(ins.instruction, Measure):
                for qubit in ins.qubits:
                    measured_qubits.add(qubit)

        for _, qubit in self._qubits.items():
            if qubit not in measured_qubits:
                self.append(Measure(), qubit)

    # pylint: disable=too-many-branches
    def assign_parameters(
            self,
            values: dict[str | Parameter, float | int] | Sequence[float | int] = None,
            inplace: bool = False,
            cache_params: bool = False,
            **kwargs
    ):
        """
        Sets the values of specified parameters in the quantum circuit.
        This method allows parameters to be set using a dictionary or
        directly via keyword arguments.

        Args:
            values (dict[str | Parameter, float | int], optional): A
                dictionary where keys are parameters (either as Parameter
                objects or their string identifiers) and values are the
                numerical values (float or int) to set. If a parameter is
                specified as a string, it must be a valid identifier and
                already exist in the circuit's parameter list.
            inplace (bool): create new circuit or not?
            cache_params (bool): cache parameters or not? for SimpleSimulator value cache.
            **kwargs: Additional parameters and their values provided as
                keyword arguments. This is useful for directly setting values
                when calling the method.

        Example:
            >>> from cqlib.circuits import Circuit, Parameter
            >>> import numpy
            >>> params = [Parameter(f'theta_{i}') for i in range(3)]
            >>> circuit = Circuit(2, parameters=params)
            >>> circuit.rx(0, params[0])
            >>> circuit.ry(0, params[0] + params[1] * params[2])
            >>> circuit.qcis
            'RX Q0 theta_0\nRY Q0 theta_0 + theta_1*theta_2'
            >>> c1 = circuit.assign_parameters({'theta_0': 1, 'theta_1': 2, 'theta_2': 0.2})
            >>> c1.qcis
            RX Q0 1\nRY Q0 1.4
            >>> c2 = circuit.assign_parameters([0.1, 2, 0.2])
            >>> c2.qcis
            RX Q0 0.1\nRY Q0 0.5
            >>> c3 = circuit.assign_parameters(theta_0=1, theta_1=0.2, theta_2=0.3)
            >>> c3.qcis
            'RX Q0 1\nRY Q0 1.06'
            >>> c4 = circuit.assign_parameters(theta_1=2)
            >>> c4.qcis
            'RX Q0 theta_0\nRY Q0 theta_0 + 2*theta_2'
            >>> c5 = circuit.assign_parameters(numpy.array([1, 2, 0.2]))
            >>> c5.qcis
            'RX Q0 1\nRY Q0 1.4'

        This method updates the internal dictionary of parameters to
        reflect the new values, allowing these parameters to be used
        with their new values in subsequent operations within the circuit.
        """
        if inplace:
            target = self
        else:
            target = self.copy()

        if values is None:
            values = {}
        if isinstance(values, ArrayLike):
            # Array like type, list/tuple/np.ndarray/torch.Tensor
            if lv := len(values) != len(self._parameters):
                raise ValueError(f"Length of values {lv} does not match "
                                 f"the number of parameters {len(self._parameters)}.")
            values = dict(zip(self._parameters, values))
        values.update(kwargs)
        for param, value in values.items():
            if isinstance(param, str):
                param = Parameter(param)
            if param not in target.parameters_value:
                raise KeyError(f"Parameter {param} not found.")

            # pylint: disable=protected-access
            target._parameters[param] = value
            if cache_params and not inplace:
                self._parameters[param] = value

        for item in target.circuit_data:
            instruction = item.instruction
            if instruction.params:
                ps = []
                for p in instruction.params:
                    if p in target.parameters_value and target.parameters_value[p] is not None:
                        p = target.parameters_value[p]
                    elif isinstance(p, Parameter):
                        p = p.value(target.parameters_value)
                        if p.is_Number:
                            p = float(p)
                        elif p.is_symbol or isinstance(p, sympy.Basic):
                            p = Parameter(p)
                    ps.append(p)
                instruction.params = ps
        return target

    @property
    def qcis(self) -> str:
        """
        Generates a qcis string of all instructions in the circuit.
        """
        return self._export_circuit_str(self._circuit_data, True, self._parameters)

    def as_str(self, qcis_compliant: bool = False):
        """
        Exports the circuit as a string format, with an option to make the output QCIS-compliant.

        Args:
            qcis_compliant (bool): If True, the output will conform to QCIS standards;
             if False, it will retain the original format with composite gates.
        """
        params = self._parameters
        return self._export_circuit_str(self._circuit_data, qcis_compliant, params)

    # pylint: disable=too-many-branches
    @classmethod
    def _export_circuit_str(
            cls,
            instructions: list[InstructionData],
            qcis_compliant: bool = False,
            params=None
    ):
        """
        Exports the circuit as a string format, with an option to make the output QCIS-compliant.

        Args:
            instructions: A list of InstructionData.
            qcis_compliant (bool): If True, the output will conform to QCIS standards;
             if False, it will retain the original format with composite gates.
        """
        if params is None:
            params = {}
        ops = []
        for instruction_data in instructions:
            instruction = instruction_data.instruction
            qubits = instruction_data.qubits

            if not isinstance(instruction, Instruction) or instruction.num_qubits != len(qubits):
                raise ValueError(f"Instruction {instruction.name} configuration error"
                                 f" with qubits {qubits}")
            if qcis_compliant and not instruction.is_supported_by_qcis:
                ops.append(cls._export_circuit_str(instruction.to_qcis(qubits), qcis_compliant))
                continue

            line = [instruction.name] + [str(qubit) for qubit in qubits]
            for param in instruction.params:
                if isinstance(param, Parameter):
                    value = param.value(params)
                    if value.is_Integer:
                        value = int(value)
                    elif value.is_Float:
                        value = float(value)
                    else:
                        value = sympy.sstr(value).replace(' ', '')
                else:
                    value = param
                if isinstance(value, (Number, Decimal, np.number)):
                    value = str(value)
                    if '.' in value:
                        value = value.rstrip('0').rstrip('.')
                line.append(value)
            ops.append(' '.join(line))
        return '\n'.join(ops)

    @classmethod
    def load(cls, qcis: str) -> Circuit:
        """
        Loads a quantum circuit from a QCIS string.

        Args:
            qcis (str): A string containing quantum circuit instructions, where each line
                        represents a circuit operation. The format for each line is
                        "GATE QUBITS [PARAMETERS]", e.g., "H Q0 Q1", "CX Q0 Q1", "RZ Q0 0.5".

        Returns:
            Circuit: A quantum circuit object constructed based on the input string.

        Raises:
            ValueError: If the input string is improperly formatted or contains
                unknown gate operations.

        Example:
            >>> circuit_description = "H Q0\\nCX Q0 Q1\\nM Q0"
            >>> c = Circuit.load(circuit_description)
            >>> print(c)
            Circuit with 3 instructions
        """
        circuit = cls(qubits=[])
        line_pattern = re.compile(r'^([A-Z][A-Z0-9]*)\s+((?:Q[0-9]+\s*)+)(.*)$')

        for line in qcis.split('\n'):
            # Delete comments `#` `//`.
            line = re.sub(r'(#|//).*', '', line).strip()
            if not line:
                continue
            match = line_pattern.match(line)
            if not match:
                raise ValueError(f'Invalid instruction format: {line}')
            gate, qubits_str, params_str = match.groups()
            qubits = circuit._parse_qubits_str(qubits_str)
            params = []
            for param in params_str.strip().split():
                try:
                    params.append(float(param))
                except ValueError:
                    s = sympy.simplify(param)
                    if s.free_symbols:
                        for symbol in s.free_symbols:
                            symbol = Parameter(str(symbol))
                            if symbol not in circuit._parameters:
                                circuit.add_parameter(symbol)
                    params.append(Parameter(s))
            circuit._process_instruction(gate, qubits, params)
        return circuit

    def _parse_qubits_str(self, qubits_str: str) -> list[Qubit]:
        """
        Parses and initializes standard qubit identifiers from QCIS instruction.

        Converts space-separated qubit tokens (Q-prefixed) into Qubit objects,
        creating new instances only when encountering previously unseen qubits.

        Args:
            qubits_str(str): Raw qubit specification segment from QCIS line.

        Returns:
            list[Qubit]: Initialized Qubit objects in order of appearance.
        """
        qubits = []
        for q_str in qubits_str.split():
            if q_str.startswith('Q'):
                qubit = self._qubits.setdefault(q_str, Qubit(int(q_str[1:])))
                qubits.append(qubit)
            else:
                raise ValueError(f"Invalid qubit format: {q_str}")
        return qubits

    def _process_instruction(self, gate: str, qubits: list, params: list):
        """
        Core dispatcher for converting parsed components into circuit operations.

        Args:
            gate: Uppercase gate identifier (e.g., 'H', 'CX', 'RZ')
            qubits: Qubit targets from prior parsing stage
            params: Numerical parameters for parameterized gates
        """
        if gate == 'M':
            for qubit in qubits:
                self.append_instruction_data(
                    InstructionData(instruction=Measure(), qubits=[qubit]))
        elif gate == 'B':
            self.append_instruction_data(
                InstructionData(instruction=Barrier(len(qubits)), qubits=qubits))
        elif hasattr(gates, gate):
            data = InstructionData(instruction=getattr(gates, gate)(*params, label=None),
                                   qubits=qubits)
            self.append_instruction_data(data)
        else:
            raise ValueError(f"Unsupported gate: {gate}")

    def __str__(self):
        return self.as_str()

    def __add__(self, other: Circuit):
        """
        Overloads the addition operator to allow concatenation of two quantum circuits
        using the `+` operator.

        Args:
            other(Circuit): Another Circuit instance to be concatenated with the current circuit.

        Returns:
            Circuit: A new Circuit object containing the combined qubits, parameters, and
            instruction sequences of both circuits.

        """
        qubits = list(set(self.qubits + other.qubits))
        params = list(set(self.parameters + other.parameters))
        circuit = Circuit(qubits=qubits, parameters=params)
        for inst in self.instruction_sequence:
            inst = deepcopy(inst)
            circuit.append(inst.instruction, inst.qubits)
        for inst in other.instruction_sequence:
            inst = deepcopy(inst)
            circuit.append(inst.instruction, inst.qubits)
        return circuit

    def __iadd__(self, other: Circuit):
        """
        Overloads the in-place addition operator to append another quantum circuit to the
        current circuit using the `+=` operator.

        Args:
            other (Circuit): Another Circuit instance to be appended to the current circuit.

        Returns:
            Circuit: The modified current Circuit object (`self`) with the additional qubits,
                parameters, and instruction sequences from the other circuit.
        """
        for qubit in other.qubits:
            if qubit not in self.qubits:
                self.add_qubit(qubit)
        self_params = [str(p) for p in self.parameters]
        other_params = [str(p) for p in other.parameters]
        for param in other_params:
            if param not in self_params:
                self.add_parameter(param)
        for inst in other.instruction_sequence.copy():
            inst = deepcopy(inst)
            self.append(inst.instruction, inst.qubits)
        return self

    def to_qasm2(self) -> str:
        """
        Convert the Circuit object to an OpenQASM 2.0 formatted string.

        Example:
            >>> circuit = Circuit(1)
            >>> circuit.h(0)
            >>> # Add gates and operations to the circuit
            >>> qasm_code = circuit.to_qasm2()
            >>> print(qasm_code)
        """
        # pylint: disable=import-outside-toplevel
        from cqlib.utils.qasm2 import dumps

        return dumps(self)

    def copy(self) -> Circuit:
        """
        Copy the circuit.
        """
        circuit = Circuit(qubits=self.qubits, parameters=self.parameters)
        for item in self._circuit_data:
            circuit.append(item.instruction.copy(), qubits=item.qubits)
        return circuit

    def draw(
            self,
            category='text',
            qubit_order: list[int | Qubit] | None = None,
            **kwargs
    ):
        """
        Draws the quantum circuit in the specified format.

        Args:
            category (str): The type of drawing to produce. Supported categories are:
                - 'text': Draws the circuit as ASCII art.
                - 'mpl': Draws the circuit using Matplotlib for a graphical representation.
            qubit_order (list[int | Qubit], optional): A list specifying the order of qubits
                in the output. If None, the default order is used.
            **kwargs: Additional keyword arguments that are passed to the specific drawing
                function.

        Returns:
            The return value depends on the selected category:
            - For 'text', it returns a string representing the circuit in text format.
            - For 'mpl', it typically displays or returns a Matplotlib figure object.

        Raises:
            ValueError: If an unsupported category is provided.
        """
        if category == 'text':
            # pylint: disable=import-outside-toplevel
            from cqlib.visualization.circuit.text import draw_text
            return draw_text(self, qubit_order=qubit_order, **kwargs)
        if category == 'mpl':
            # pylint: disable=import-outside-toplevel
            from cqlib.visualization.circuit.mpl import draw_mpl
            return draw_mpl(self, qubit_order=qubit_order, **kwargs)
        raise VisualizationError(f"Unsupported category: {category}")
