# This code is part of cqlib.
#
# Copyright (C) 2025 China Telecom Quantum Group, QuantumCTek Co., Ltd.,
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
Quantum circuit visualization
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterator

import numpy as np

from cqlib.circuits.bit import Bit
from cqlib.circuits.qubit import Qubit
from cqlib.circuits.circuit import Circuit
from cqlib.circuits.dag import circuit_to_dag, topological_layers
from cqlib.circuits.instruction import Instruction
from cqlib.circuits.instruction_data import InstructionData
from cqlib.exceptions import CqlibError
from cqlib.utils.pi_check import pi_check

logger = logging.getLogger('cqlib.vis')


class BoxChar(str, Enum):
    """
    Unicode box-drawing characters collection for circuit visualization
    """
    TOP = '╵'
    BOTTOM = '╷'
    LEFT = '╴'
    RIGHT = '╶'
    TOP_BOTTOM = '│'
    LEFT_RIGHT = '─'

    TOP_LEFT = '┘'
    TOP_RIGHT = '└'
    BOTTOM_LEFT = '┐'
    BOTTOM_RIGHT = '┌'

    TOP_BOTTOM_LEFT = '┤'
    TOP_BOTTOM_RIGHT = '├'
    TOP_LEFT_RIGHT = '┴'
    BOTTOM_LEFT_RIGHT = '┬'
    TOP_BOTTOM_LEFT_RIGHT = '┼'

    DOT = '■'
    CONNECT = 'X'
    LEFT_ARROW = '«'
    RIGHT_ARROW = '»'


class BaseDrawer(ABC):
    """
    Abstract Quantum circuit Drawer.
    """
    MIN_LINE_WIDTH = 10
    DEFAULT_LINE_WIDTH = 30

    def __init__(
            self,
            circuit: Circuit,
            qubit_order: list[int | Bit] | None = None,
    ):
        """
        Initialization Parameters

        Args:
            circuit(Circuit): Quantum circuit to be visualized
            qubit_order(list[int | Bit] | None): Optional list specifying the display
                order of qubits
        """
        self.circuit = circuit
        self.qubit_order = qubit_order
        self.sorted_qubits: list[Bit] = []
        self.qubit_mapping: dict[Bit, int] = {}

        self.order_qubits()

    def order_qubits(self):
        """
        Determines the display order of qubits and initializes related attributes.
        Uses specified qubit_order if provided (supplementing with remaining circuit qubits),
        otherwise sorts qubits by their indices. Initializes:
        - sorted_qubits: List of qubits in display order
        - qubit_mapping: Dictionary mapping qubits to display line numbers
        """
        if self.qubit_order is None:
            sorted_qubits = sorted(self.circuit.qubits, key=lambda s: s.index)
        else:
            sorted_qubits = [q if isinstance(q, Qubit) else Qubit(q) for q in self.qubit_order]
            for qubit in self.circuit.qubits:
                if qubit not in sorted_qubits:
                    sorted_qubits.append(qubit)
        self.sorted_qubits = sorted_qubits
        self.qubit_mapping = {q: i * 2 + 1 for i, q in enumerate(sorted_qubits)}

    def generate_moment(self) -> Iterator[list[InstructionData]]:
        """
        Generates an iterator of topological layers (moments) from the circuit DAG.
        Each moment contains non-overlapping operations that can be executed in parallel.

        Yields:
            list[InstructionData]: A moment containing parallel-compatible operations

        Raises:
            CqlibError: If qubit conflicts are detected within a topological layer
        """
        dag_circuit = circuit_to_dag(self.circuit)
        for layer in topological_layers(dag_circuit):
            moment = []
            used_qubits = set()
            for node_id in layer:
                node: InstructionData = dag_circuit.get_node_data(node_id)
                if any(q in used_qubits for q in node.qubits):
                    raise CqlibError(f"Qubit conflict in topological layer: {node.qubits}")
                used_qubits.update(node.qubits)
                moment.append(node)
            yield moment

    @staticmethod
    def moment_to_columns(moment: list[InstructionData]) -> list[list[InstructionData]]:
        """
        Organizes a moment into display columns by analyzing qubit ranges.
        Operations with overlapping qubit ranges are placed in separate columns.

        Args:
            moment (list[InstructionData]): A collection of operations from one topological layer

        Returns:
            list[list[InstructionData]]: Column-based structure for visualization,
            where each sublist represents a display column
        """

        qubit_ranges = []
        qubit_min_to_ins = {}
        for ins in moment:
            qubits_index = [q.index for q in ins.qubits]
            qubit_min_to_ins[min(qubits_index)] = ins
            qubit_ranges.append([min(qubits_index), max(qubits_index)])

        moment_columns = []
        for qubit_range in qubit_ranges:
            min_index, max_index = qubit_range
            for column in moment_columns:
                for item in column:
                    mi, ma = item
                    if max_index >= mi and min_index <= ma:
                        break
                else:
                    column.append(qubit_range)
                    break
            else:
                moment_columns.append([qubit_range])
        return [[qubit_min_to_ins[r[0]] for r in col] for col in moment_columns]

    def qubit_line_no(self, qubit: Bit) -> int:
        """
        Retrieves the display line number for a given qubit in the visualization

        Args:
            qubit (Qubit): Target qubit to query

        Returns:
            int: Odd-numbered line position corresponding to the qubit's display order
        """
        return self.qubit_mapping[qubit]

    @abstractmethod
    def drawer(self) -> str:
        """ start draw lines"""

    @abstractmethod
    def draw_column(self, column) -> list[list[str]]:
        """ draw column lines"""

    @staticmethod
    def _str_instruction(ins: Instruction) -> str:
        """
        Converts an InstructionData object to a formatted string representation.
        """
        if not ins.params:
            return ins.name
        return f'{ins.name}({BaseDrawer._str_params(ins)})'

    @staticmethod
    def _str_params(ins: Instruction):
        ps = []
        for p in ins.params:
            if isinstance(p, (float, int, np.floating)):
                t = pi_check(p)
            else:
                t = p
            ps.append(str(t))
        return ','.join(ps)
