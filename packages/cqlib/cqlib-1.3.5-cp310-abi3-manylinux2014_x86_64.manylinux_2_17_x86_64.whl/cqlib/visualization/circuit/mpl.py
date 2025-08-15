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
Matplotlib quantum circuit drawer module
"""

import logging
from collections.abc import Sequence
from enum import IntEnum

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Arc

from cqlib.circuits.barrier import Barrier
from cqlib.circuits.bit import Bit
from cqlib.circuits.circuit import Circuit
from cqlib.circuits.instruction_data import InstructionData
from cqlib.circuits.gates import SWAP, CZ
from cqlib.circuits.gates.gate import ControlledGate
from cqlib.circuits.measure import Measure
from cqlib.circuits.qubit import Qubit
from cqlib.exceptions import CqlibError

from .base import BaseDrawer, BoxChar
from .style import Style

logger = logging.getLogger('cqlib.vis')


class ZOrder(IntEnum):
    """
    Defines z-order layers for rendering circuit components.

    Ensures proper layering of visual elements (e.g., lines under boxes).

    Members:
        LINE (int): Layer for quantum wires and connectors (z=10)
        BOX (int): Layer for gate background boxes (z=20)
        GATE (int): Layer for gate symbols and text (z=30)
    """
    LINE = 10
    BOX = 20
    GATE = 30


# pylint: disable=too-many-instance-attributes
class MatplotlibDrawer(BaseDrawer):
    """
    Quantum circuit visualizer using Matplotlib.

    Renders circuit diagrams with customizable styling and layout. Supports
    multi-qubit gates, parameterized operations, and classical registers.
    """
    figure_styles = {
        'figure_color': 'white',
        'axes_color': 'white',
        'show_axis': '0',
        'margin_top': 0.88,
        'margin_bottom': 0.11,
        'margin_left': 0.125,
        'margin_right': 0.9,
        'moment_width': 0.3,
        'gate_width': 0.8,
        'gate_height': 1.2,
    }

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
            self,
            circuit: Circuit,
            qubit_order: list[int | Qubit] | None = None,
            figure_styles: dict[str, str | bool | float | tuple[float | int]] | None = None,
            gate_styles: dict[str, str | bool | float | tuple[float | int]] | None = None,
            title: str | None = None,
            fonts: str | list[str] | None = None,
            filename: str | None = None,
            style: str = 'default',
    ):
        """
        Initialization Parameters

        Args:
            circuit (Circuit): Quantum circuit to visualize.
            qubit_order (list[int | Qubit] | None): Custom display order for qubits.
                Defaults to circuit's natural ordering.
            figure_styles (dict | None): Overrides for default figure styles.
            gate_styles (dict | None): Overrides for default gate rendering styles.
            title (str | None): Title displayed above the circuit.
            fonts (str | list[str] | None): Font family/families for text rendering.
            filename (str, optional): Optional filename to save the diagram to.
        """
        super().__init__(circuit, qubit_order)

        self.gate_style = Style(style, gate_styles)
        if figure_styles:
            self.figure_styles.update(figure_styles)

        if fonts and isinstance(fonts, str):
            fonts = [fonts]
        self._fonts = fonts
        self._title = title
        self._filename = filename
        self._fig = None
        self._ax = None
        self._real_line_width = 1
        self._current_x = 0
        self._current_col_index = 0
        self._current_moment_index = 0
        self.column_width = []
        self.qubit_mapping = {q: i * 2 for i, q in enumerate(self.sorted_qubits)}

    def drawer(self) -> Figure:
        """
        Generates complete circuit visualization.

        Processes circuit structure, computes layout, and renders all components.

        Returns:
            Figure: Matplotlib figure containing circuit diagram
        """
        lines = self._make_lines()

        self._fig, self._ax = self.setup_figure()
        for i, qubit in enumerate(self.sorted_qubits):
            self._ax.text(-0.6, i * 2, str(qubit), ha='right', va='center',
                          fontsize=12, color='black')
            self._ax.hlines(i * 2, xmin=-self.figure_styles['moment_width'],
                            xmax=self._real_line_width, color='gray', linewidth=1)
        self._current_x = 0
        for moment in lines:
            start = self._current_x
            for column in moment['moment']:
                column_width = column['width']
                self._current_x += column_width / 2
                self.draw_column(column['column'])
                self._current_x += column_width / 2
            # Draw light gray background area when multiple parallel gate
            # columns exist in the same moment
            if len(moment['moment']) > 1:
                self._ax.axvspan(
                    xmin=start - 0.1,
                    xmax=self._current_x + 0.1,
                    color='lightgray',
                    alpha=0.2,
                    zorder=0
                )
            self._current_x += self.figure_styles['moment_width']
        if self._filename:
            self._fig.savefig(self._filename, transparent=None, dpi='figure', )
        return self._fig

    def _make_lines(self):
        """
        Organizes circuit moments into columns for rendering. Internal layout logic.
        """
        lines = []

        for moment in self.generate_moment():
            columns = []
            max_width = 0
            for column in self.moment_to_columns(moment):
                col_width = 0
                instructions = []
                for ins in column:
                    ins_width = self.figure_styles['gate_width']
                    if ins.instruction.params:
                        t = self._str_params(ins.instruction)
                        ins_width = max(ins_width, len(t) / 5.0 * self.figure_styles['gate_width'])
                    instructions.append({
                        'width': ins_width,
                        'instruction': ins
                    })
                    col_width = max(ins_width, col_width)
                self._real_line_width += col_width
                columns.append({
                    'width': col_width,
                    'column': instructions
                })
                max_width += col_width
            self._real_line_width += self.figure_styles['moment_width']
            lines.append({
                'width': max_width,
                'moment': columns
            })
        return lines

    def setup_figure(self) -> tuple[Figure, Axes]:
        """
        Configures Matplotlib figure and axes with specified styles.

        Returns:
            tuple[Figure, Axes]: Configured figure and axes objects.
        """
        fig, ax = plt.subplots(figsize=(self._real_line_width, len(self.sorted_qubits)))
        fig.set_facecolor(self.figure_styles['figure_color'])
        ax.set_facecolor(self.figure_styles['axes_color'])
        plt.subplots_adjust(
            left=self.figure_styles['margin_left'],
            right=self.figure_styles['margin_right'],
            top=self.figure_styles['margin_top'],
            bottom=self.figure_styles['margin_bottom']
        )
        ax.set_xlim(-1, self._real_line_width - 1)
        ax.set_ylim(-1, len(self.sorted_qubits) * 2 - 1)
        ax.invert_yaxis()
        if self._title:
            ax.set_title(self._title, loc='center')

        ax.axis(self.figure_styles['show_axis'] in [1, True, 'true', '1'])
        if self._fonts:
            plt.rcParams['font.sans-serif'] = self._fonts
        plt.rcParams['axes.unicode_minus'] = False

        return fig, ax

    def draw_column(self, column: list[dict]):
        """
        Renders a single column of instructions onto the axes.

        Args:
            column (list[InstructionData]): Group of gates to draw vertically aligned.
        """
        for item in column:
            ins_width = item['width']
            ins = item['instruction']
            if len(ins.qubits) == 1:
                self._draw_single_gate(ins, ins_width)
            else:
                self._draw_multi_gate(ins, ins_width)

    def _draw_single_gate(
            self,
            instruction_data: InstructionData,
            width: float,
            gate_style=None
    ):
        """
        Renders single-qubit gate with parameter display.

        Args:
            instruction_data (InstructionData): Gate and associated qubit(s).
        """
        qubit_no = self.qubit_line_no(instruction_data.qubits[0])
        if gate_style:
            gs = gate_style
        else:
            gs = self.gate_style[instruction_data.instruction.name]

        rect = Rectangle(
            (self._current_x - width / 2, qubit_no - self.figure_styles['gate_height'] / 2),
            width,
            self.figure_styles['gate_height'],
            fc=gs['background_color'],
            ec=gs['border_color'],
            lw=2,
            zorder=ZOrder.BOX
        )
        self._ax.add_patch(rect)
        ins = instruction_data.instruction

        if isinstance(ins, Measure):
            self._draw_measure(qubit_no)
            return
        if ins.params:
            t = f"{ins.name}\n{self._str_params(ins)}"
        else:
            t = ins.name

        self._ax.text(
            self._current_x,
            qubit_no,
            t,
            ha='center',
            va='center',
            fontsize=gs['font_size'],
            color=gs['text_color'],
            zorder=ZOrder.GATE
        )

    def _draw_measure(self, qubit_no: int):
        """
        Draws a measurement symbol on the circuit diagram.

        Args:
            qubit_no (int): Line number for the qubit where measurement is performed.
        """
        gs = self.gate_style['M']
        self._ax.add_patch(Arc(
            (self._current_x, qubit_no + 0.3 * self.figure_styles['gate_height']),
            width=0.5 * self.figure_styles['gate_width'],
            height=0.8 * self.figure_styles['gate_width'],
            theta1=180,
            theta2=0,
            lw=2,
            color=gs['text_color'],
            zorder=ZOrder.GATE,
        ))

        self._ax.arrow(
            x=self._current_x - 0.1 * self.figure_styles['gate_width'],
            y=qubit_no + 0.5,
            dx=0.2 * self.figure_styles['gate_width'],
            dy=-0.6 * self.figure_styles['gate_height'],
            head_width=self.figure_styles['gate_width'] / 9.0,
            zorder=ZOrder.GATE,
            color=gs['text_color'],
            length_includes_head=False
        )

    def _draw_multi_gate(self, instruction_data: InstructionData, width: float):
        """
        Draws multi-qubit gates with connection lines.
        Args:
            instruction_data (InstructionData): Gate and associated qubits.
            width (float): Width of the gate column.
        """
        qs = instruction_data.qubits
        instruction = instruction_data.instruction
        if isinstance(instruction, SWAP):
            self._draw_swap(qs)
        elif isinstance(instruction, CZ):
            self._draw_cz(qs)
        elif isinstance(instruction, Barrier):
            self._draw_barrier(qs)
        elif isinstance(instruction, ControlledGate):
            self._draw_controlled_gate(instruction_data, width)

    def _draw_swap(self, qs: Sequence[Bit]):
        gs = self.gate_style['SWAP']
        for q in qs:
            self._ax.plot(
                [self._current_x - 0.3, self._current_x + 0.3],
                [self.qubit_line_no(q) + 0.3, self.qubit_line_no(q) - 0.3],
                color=gs['text_color'],
                linewidth=gs['line_width'],
                zorder=ZOrder.GATE,
            )
            self._ax.plot(
                [self._current_x - 0.3, self._current_x + 0.3],
                [self.qubit_line_no(q) - 0.3, self.qubit_line_no(q) + 0.3],
                color=gs['text_color'],
                linewidth=1.5,
                zorder=ZOrder.GATE,
            )

        self._ax.vlines(
            self._current_x,
            ymin=self.qubit_line_no(qs[0]),
            ymax=self.qubit_line_no(qs[1]),
            color=gs['line_color'],
            linewidth=gs['line_width']
        )

    def _draw_barrier(self, qs: Sequence[Bit]):
        gs = self.gate_style['B']
        for q in qs:
            self._ax.vlines(
                self._current_x,
                ymin=self.qubit_line_no(q) - 1,
                ymax=self.qubit_line_no(q) + 1,
                # linestyles='dashed',
                color=gs['line_color'],
                linestyles=(0, (10, 3)),
                linewidth=gs['line_width']
            )

    def _draw_cz(self, qs: Sequence[Bit]):
        gs = self.gate_style['CZ']
        for q in qs:
            self._ax.text(
                self._current_x,
                self.qubit_line_no(q),
                BoxChar.DOT.value,
                ha='center',
                va='center',
                color=gs['line_color'],
                fontsize=12,
                zorder=ZOrder.GATE,
            )
        self._ax.vlines(
            self._current_x,
            ymin=self.qubit_line_no(qs[0]),
            ymax=self.qubit_line_no(qs[1]),
            color=gs['line_color'],
            linewidth=1
        )

    def _draw_controlled_gate(self, instruction_data: InstructionData, width: float):
        """
        Renders controlled gates with connection lines.

        Args:
            instruction_data: Must contain a ControlledGate instance
        """
        gs = self.gate_style[instruction_data.instruction.name]
        if not isinstance(instruction_data.instruction, ControlledGate):
            raise CqlibError(f"Invalid instruction type for controlled gate. {instruction_data}")
        qubit_nos = []
        for i, qubit in enumerate(instruction_data.qubits):
            qubit_nos.append(self.qubit_line_no(qubit))
            if i in instruction_data.instruction.control_index:
                self._ax.text(
                    self._current_x,
                    self.qubit_line_no(qubit),
                    BoxChar.DOT.value,
                    ha='center',
                    va='center',
                    color=gs['line_color'],
                    fontsize=12,
                    zorder=ZOrder.GATE,
                )
            else:
                self._draw_single_gate(
                    InstructionData(instruction_data.instruction.base_gate, [qubit]),
                    gate_style=gs,
                    width=width
                )
        self._ax.vlines(
            self._current_x,
            ymin=min(qubit_nos),
            ymax=max(qubit_nos),
            color=gs['line_color'],
            linewidth=1,
            zorder=ZOrder.LINE
        )


# pylint: disable=too-many-arguments, too-many-positional-arguments
def draw_mpl(
        circuit: Circuit,
        title: str | None = None,
        filename: str | None = None,
        qubit_order: list[int | Qubit] | None = None,
        figure_styles: dict[str, str | bool | float | tuple[float | int]] | None = None,
        gate_styles: dict[str, str | bool | float | tuple[float | int]] | None = None,
        fonts: str | list[str] | None = None,
        style: str = 'default',
) -> Figure:
    """
    Quick visualization entry point.

    Args:
        circuit(Circuit): Quantum circuit to draw
        title (str | None): Optional diagram title
        filename (str | None): Optional filename to save the diagram
        qubit_order (list[int | Qubit] | None): Custom display order for qubits.
            Defaults to circuit's natural ordering.
        figure_styles (dict | None): Overrides for default figure styles (colors, margins, etc.).
        gate_styles (dict | None): Overrides for default gate rendering styles.
        fonts (str | list[str] | None): Font family/families for text rendering.
        style (str): Style name for consistent visual appearance.

    Returns:
        Figure: Ready-to-display circuit visualization
    """
    return MatplotlibDrawer(
        circuit,
        title=title,
        filename=filename,
        figure_styles=figure_styles,
        qubit_order=qubit_order,
        gate_styles=gate_styles,
        fonts=fonts,
        style=style
    ).drawer()
