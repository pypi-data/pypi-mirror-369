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
Handles circuit visualization styles by loading from JSON files and allowing customizations.

This module provides the Style class which manages gate display styles loaded from
JSON files in the styles directory, with optional runtime customizations.
"""
import json
from pathlib import Path


class Style:
    """
    Manages visualization styles for quantum circuit gates.

    Styles are loaded from JSON files and can be customized at runtime. Each style
    defines graphical parameters for different types of quantum gates.

    Args:
        style: Name of the base style JSON file (without extension)
        gate_styles: Optional dictionary of style overrides to merge with base style

    Attributes:
        _style: Combined dictionary of all style parameters
    """

    def __init__(self, style: str, gate_styles: dict | None = None):
        """Initialize style with base configuration and optional customizations."""
        self._style = self.load_style(style)
        if gate_styles:
            self._style.update(gate_styles)

    @staticmethod
    def load_style(style):
        """
        Load style configuration from JSON file in styles directory.

        Args:
            style: Name of the style file (without .json extension)

        Returns:
            dict: Style parameters loaded from JSON file

        Raises:
            ValueError: If the specified style file doesn't exist
        """
        path = Path(__file__).parent / "styles" / f'{style}.json'
        if not path.exists():
            raise ValueError(f"Style {style} not found.")
        with open(path, 'r', encoding='utf-8') as f:
            gate_styles = json.load(f)
        return gate_styles

    def __getitem__(self, item: str):
        """Retrieve style parameters for a specific gate type.

        Falls back to 'default' style if gate-specific parameters aren't found.

        Args:
            item: Name of the gate type to retrieve style for

        Returns:
            dict: Style parameters for the requested gate type
        """
        if item in self._style:
            return self._style[item]
        return self._style['default']
