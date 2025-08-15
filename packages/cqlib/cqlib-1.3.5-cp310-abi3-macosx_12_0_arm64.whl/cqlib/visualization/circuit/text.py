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
Text-based quantum circuit visualization module

Provides ASCII/Unicode art representation of quantum circuits using box-drawing characters.
"""
import copy
import logging
import shutil

from cqlib.circuits.circuit import Circuit
from cqlib.circuits.gates import SWAP, CZ
from cqlib.circuits.barrier import Barrier
from cqlib.circuits.gates.gate import ControlledGate
from cqlib.circuits.instruction_data import InstructionData
from cqlib.circuits.qubit import Qubit

from .base import BaseDrawer, BoxChar

logger = logging.getLogger('cqlib.vis')


class TextDrawer(BaseDrawer):
    """
    Renders quantum circuits as text diagrams using box-drawing characters
    """

    def __init__(
            self,
            circuit: Circuit,
            qubit_order: list[int | Qubit] | None = None,
            line_width: int | None = None,
    ):
        """
        Initialization Parameters

        Args:
            circuit (Circuit): Quantum circuit to visualize
            qubit_order (list[int | Qubit] | None): Custom ordering of qubits.
            line_width(int | None): Optional width of the visualization output
        """
        super().__init__(circuit, qubit_order)
        self.line_width = line_width

    def drawer(self) -> str:
        """
        Generates the complete text-based circuit diagram.

        Returns:
            str: Full circuit representation characters.
        """
        max_line_width = self.get_line_width()
        lines = self.make_lines()
        data = []
        lines_count = len(self.sorted_qubits) * 2 + 1
        start_qubits = copy.deepcopy(lines[0])
        current_data = [lines[0][i] for i in range(lines_count)]
        current_width = 0
        for moment in lines[1:]:

            moment_len = len(''.join(moment[0]))
            if moment_len + current_width > max_line_width:
                data.append(current_data)
                for d in current_data:
                    d.append(BoxChar.RIGHT_ARROW)
                current_data = []
                for i in range(lines_count):
                    s = [BoxChar.LEFT_ARROW]
                    s.extend(start_qubits[i])
                    current_data.append(s)
                current_width = 0
            for i, line in enumerate(moment):
                current_data[i].extend(line)
            current_width += moment_len
        data.append(current_data)
        t = []
        for lines in data:
            for line in lines:
                t.extend(line)
                t.append('\n')
            t.append('\n')
        return ''.join(t)

    # pylint: disable=too-many-locals
    def make_lines(self) -> list[list[list[str]]]:
        """
        Constructs the circuit visualization line structure.

        Builds a 3-level nested list representing the circuit layout:
        - Outer list: Moments (vertical slices of parallel operations)
        - Middle list: Text lines per moment (including qubit labels and connections)
        - Inner list: Character sequences for each line segment

        Returns:
            List of moments, each containing lists of text lines with box characters.
            Structure details:
            - Even indices: Spacer lines between qubits
            - Odd indices: Qubit lines with labels and gate symbols
            - First element: Initial qubit label headers
            - Subsequent elements: Circuit moments with gate representations
        """
        lines = []
        qubit_len = max(len(str(q.index)) for q in self.sorted_qubits)
        empty_line = ' ' * (qubit_len + 6)
        lines_count = len(self.sorted_qubits) * 2 + 1
        # qubits
        start_lines = []
        for qubit in self.sorted_qubits:
            start_lines.extend([
                [empty_line],
                [''.join([' ', f'Q{qubit.index}'.rjust(qubit_len + 1),
                          ': ', BoxChar.LEFT_RIGHT * 2])]
            ])
        start_lines.append([empty_line])
        lines.append(start_lines)

        # instructions
        for moment in self.generate_moment():
            # before moment, add one symbol
            moment_lines = [[BoxChar.LEFT_RIGHT if i % 2 == 1 else ' '] for i in range(lines_count)]

            # drawer one moment, maybe multi columns
            columns = self.moment_to_columns(moment)
            for column in columns:
                column_lines = self.draw_column(column)
                for line_i, line in enumerate(column_lines):
                    moment_lines[line_i].extend(line)

            # after moment, add one symbol
            for i, line in enumerate(moment_lines):
                line.append(BoxChar.LEFT_RIGHT if i % 2 == 1 else ' ')

            # mark many column as one moment
            col_len = len(columns)
            if col_len > 1:
                s = BoxChar.LEFT_RIGHT * (len(''.join(moment_lines[0])) - 2)
                moment_lines[0] = [BoxChar.BOTTOM_RIGHT, s, BoxChar.BOTTOM_LEFT]
                moment_lines[-1] = [BoxChar.TOP_RIGHT, s, BoxChar.TOP_LEFT]
            lines.append(moment_lines)
        return lines

    def draw_column(self, column: list[InstructionData]):
        """
        Processes a vertical column of parallel operations

        Args:
            column: Group of non-overlapping operations from the same moment

        Returns:
            list: Formatted lines ready for insertion into main drawing
        """
        max_width = 1

        # container
        lines = [[] for _ in range(len(self.sorted_qubits) * 2 + 1)]
        # draw every InstructionData
        for ins in column:
            match len(ins.qubits):
                case 1:
                    lines = self.draw_single_gate(ins, lines)
                case _:
                    lines = self.draw_multi_gate(ins, lines)
        # calculate max width
        for line in lines:
            for s in line:
                max_width = max(max_width, len(s))
        # fit max width
        empty_line = ' ' * max_width
        left_right_line = BoxChar.LEFT_RIGHT * max_width
        for i, line in enumerate(lines):
            if i % 2 == 0:
                if line:
                    lines[i] = [line[0].center(max_width)]
                else:
                    lines[i].append(empty_line)
            else:
                if line:
                    lines[i] = [line[0].center(max_width, BoxChar.LEFT_RIGHT)]
                else:
                    lines[i].append(left_right_line)

        return lines

    def draw_single_gate(self, ins: InstructionData, lines: list[list[str]]):
        """
        Handles single-qubit gate visualization

        Args:
            ins: Gate instruction to render
            lines: Current drawing lines state

        Returns:
            Updated lines with gate symbol placed on target qubit line
        """
        lines[self.qubit_line_no(ins.qubits[0])].append(self._str_instruction(ins.instruction))
        return lines

    def draw_multi_gate(self, ins: InstructionData, lines: list[list[str]]):
        """
        Visualizes multi-qubit operations with vertical connections

        Special cases:
        - SWAP: Uses 'X' connection symbols
        - CZ: Uses solid dots
        - Barriers: Vertical lines spanning involved qubits
        - Controlled gates: Differentiates control/target qubits

        Args:
            ins: Multi-qubit instruction to render
            lines: Current drawing lines state

        Returns:
            Updated lines with gate symbols and connection lines
        """
        if isinstance(ins.instruction, SWAP):
            lines[self.qubit_line_no(ins.qubits[0])].append(BoxChar.CONNECT)
            lines[self.qubit_line_no(ins.qubits[1])].append(BoxChar.CONNECT)
        elif isinstance(ins.instruction, CZ):
            lines[self.qubit_line_no(ins.qubits[0])].append(BoxChar.DOT)
            lines[self.qubit_line_no(ins.qubits[1])].append(BoxChar.DOT)
        elif isinstance(ins.instruction, Barrier):
            for qubit in ins.qubits:
                idx = self.qubit_line_no(qubit)
                if idx not in (1, len(lines) - 1):
                    lines[idx - 1].append(BoxChar.TOP_BOTTOM)
                lines[idx].append(BoxChar.TOP_BOTTOM)
            # Barrier, No vertical connections required
            return lines
        elif isinstance(ins.instruction, ControlledGate):
            for index, qubit in enumerate(ins.qubits):
                s = BoxChar.DOT if index in ins.instruction.control_index \
                    else str(ins.instruction.base_gate)
                lines[self.qubit_line_no(qubit)].append(s)

        # add connect vertical line
        qubit_index = [self.qubit_line_no(q) for q in ins.qubits]
        min_index, max_index = min(qubit_index), max(qubit_index)
        for idx in range(min_index + 1, max_index):
            lines[idx].append(BoxChar.TOP_BOTTOM_LEFT_RIGHT if idx % 2 == 1
                              else BoxChar.TOP_BOTTOM)

        return lines

    def get_line_width(self):
        """
        Determines the effective display width for circuit rendering.

        Priority order for width determination:
        1. User-specified line_width (if > MIN_LINE_WIDTH)
        2. Current terminal width
        3. DEFAULT_LINE_WIDTH fallback

        Returns:
            int: display width in characters.
        """
        if self.line_width:
            if self.line_width > self.MIN_LINE_WIDTH:
                return self.line_width
            if self.line_width < 0:
                return float('inf')
        # try to get terminal size
        width, _ = shutil.get_terminal_size()
        if not width:
            width = self.DEFAULT_LINE_WIDTH
        return width


def draw_text(
        circuit: Circuit,
        qubit_order: list[int | Qubit] = None,
        line_width: int = None,
):
    """
    Quick-access function for text circuit visualization.

    Args:
        circuit (Circuit): Quantum circuit to visualize
        qubit_order (list[int | Qubit]): Optional custom qubit arrangement
        line_width (int):

    Returns:
        str: Ready-to-print circuit diagram
    """
    return TextDrawer(circuit, qubit_order, line_width).drawer()
