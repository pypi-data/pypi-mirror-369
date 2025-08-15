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
OpenQASM 2.0 Program Loader

This module provides functions to load and parse OpenQASM 2.0 programs,
converting them into `cqlib` Circuit objects. It supports loading from
both file paths and direct OpenQASM 2.0 strings, making it convenient
to handle OpenQASM programs from different sources.
"""
import os

from cqlib.circuits.circuit import Circuit
from ._parse import OpenQASM2Converter


def load(filename: str | os.PathLike, precision: int = 10) -> Circuit:
    """
    Load an OpenQASM 2.0 program from a file and convert it to a Circuit.

    Args:
        filename(str | os.PathLike): The OpenQASM 2 program file name.
        precision (int, optional): The number of decimal places to round parameters to.
    """
    return OpenQASM2Converter(precision=precision).parse(qasm_file=filename)


def loads(qasm: str, precision: int = 10) -> Circuit:
    """
    Load an OpenQASM 2.0 program from a string and convert it to a Circuit.

    Args:
        qasm (str): OpenQASM 2.0 program as a string.
        precision (int, optional): The number of decimal places to round parameters to.
    """
    return OpenQASM2Converter(precision=precision).parse(qasm_str=qasm)
