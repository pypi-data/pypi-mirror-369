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
This module provides functions for converting angles to their symbolic representations
"""
from decimal import Decimal
from fractions import Fraction

import numpy as np

# Predefined π multiples and their symbolic representations for common angles
PI_CACHE = {
    # Fractional π values grouped by denominator
    0: '0',
    np.pi: 'π',
    2 * np.pi: '2π',
    3 * np.pi: '3π',
    4 * np.pi: '4π',
    5 * np.pi: '5π',
    6 * np.pi: '6π',
    7 * np.pi: '7π',
    8 * np.pi: '8π',
    9 * np.pi: '9π',
    10 * np.pi: '10π',
    11 * np.pi: '11π',

    # Fractional π values grouped by denominator
    np.pi / 2: 'π/2',
    np.pi * 3 / 2: '3π/2',
    np.pi * 5 / 2: '5π/2',

    np.pi / 3: 'π/3',
    np.pi * 2 / 3: '2π/3',
    np.pi * 4 / 3: '4π/3',
    np.pi * 5 / 3: '5π/3',
    np.pi * 7 / 3: '7π/3',
    np.pi * 8 / 3: '8π/3',

    np.pi / 4: 'π/4',
    np.pi * 3 / 4: '3π/4',
    np.pi * 5 / 4: '5π/4',
    np.pi * 7 / 4: '7π/4',
    np.pi * 9 / 4: '9π/4',

    np.pi / 5: 'π/5',
    np.pi * 2 / 5: '2π/5',
    np.pi * 3 / 5: '3π/5',
    np.pi * 4 / 5: '4π/5',
    np.pi * 6 / 5: '6π/5',
    np.pi * 7 / 5: '7π/5',
    np.pi * 8 / 5: '8π/5',
    np.pi * 9 / 5: '9π/5',
    np.pi * 11 / 5: '11π/5',

    np.pi / 6: 'π/6',
    np.pi * 5 / 6: '5π/6',
    np.pi * 7 / 6: '7π/6',
    np.pi * 11 / 6: '11π/6',
    np.pi * 13 / 6: '13π/6',

    np.pi / 7: 'π/7',
    np.pi * 2 / 7: '2π/7',
    np.pi * 3 / 7: '3π/7',
    np.pi * 4 / 7: '4π/7',
    np.pi * 5 / 7: '5π/7',
    np.pi * 6 / 7: '6π/7',
    np.pi * 8 / 7: '8π/7',
    np.pi * 9 / 7: '9π/7',
    np.pi * 10 / 7: '10π/7',
    np.pi * 11 / 7: '11π/7',
    np.pi * 12 / 7: '12π/7',
    np.pi * 13 / 7: '13π/7',
    np.pi * 15 / 7: '15π/7',

    np.pi / 8: 'π/8',
    np.pi * 3 / 8: '3π/8',
    np.pi * 5 / 8: '5π/8',
    np.pi * 7 / 8: '7π/8',
    np.pi * 9 / 8: '9π/8',
    np.pi * 11 / 8: '11π/8',

    np.pi / 9: 'π/9',
    np.pi * 2 / 9: '2π/9',
    np.pi * 4 / 9: '4π/9',
    np.pi * 5 / 9: '5π/9',
    np.pi * 7 / 9: '7π/9',
    np.pi * 8 / 9: '8π/9',

    np.pi / 10: 'π/10',
    np.pi * 3 / 10: '3π/10',
    np.pi * 7 / 10: '7π/10',
    np.pi * 9 / 10: '9π/10',
    np.pi * 11 / 10: '11π/10',

    np.pi / 11: 'π/11',
    np.pi * 2 / 11: '2π/11',
    np.pi * 3 / 11: '3π/11',
    np.pi * 4 / 11: '4π/11',
    np.pi * 5 / 11: '5π/11',
    np.pi * 6 / 11: '6π/11',
    np.pi * 7 / 11: '7π/11',
    np.pi * 8 / 11: '8π/11',
    np.pi * 9 / 11: '9π/11',
    np.pi * 10 / 11: '10π/11',
}


def pi_check(
        angle: float | np.floating,
        precision: float = 1e-10,
        unicode: bool = True,
) -> float | np.floating | str:
    """Convert angle value to symbolic π representation

    Args:
        angle: Input angle in radians
        precision: Relative tolerance for float comparison
        unicode: Whether to use Unicode π symbol (False uses 'pi')

    Returns:
        Symbolic expression string or original value if cannot simplify
    """
    # Handle sign and absolute value
    pi_symbol = 'π' if unicode else 'pi'
    sign = "-" if angle < 0 else ""
    abs_angle = abs(angle)

    # Check predefined cache first
    for k, v in PI_CACHE.items():
        if np.isclose(abs_angle, k, rtol=precision):
            return f"{sign}{v}" if unicode else f"{sign}{v.replace('π', 'pi')}"

    # Calculate π multiple
    k = abs_angle / np.pi

    # Check integer multiples
    integer_part = round(k)
    if np.isclose(k, integer_part, rtol=precision):
        return f"{sign}{integer_part}{pi_symbol}"

    # Attempt fractional form (π/2, π/3 ...)
    float_part = k - integer_part
    frac = Fraction(float_part).limit_denominator(1000)
    numerator = frac.numerator
    denominator = frac.denominator
    if np.isclose(numerator / denominator, float_part, rtol=precision):
        # Combine integer and fractional parts
        return f"{sign}{numerator + denominator * integer_part}{pi_symbol}/{denominator}"

    # Fallback to decimal representation (like 0.1233π ...)
    num_str = str(Decimal(str(k)))
    integer_part, decimal_part = num_str.split('.')
    if len(decimal_part) < 5:
        return f"{sign}{k}{pi_symbol}"
    # Return original value if no simplification possible
    return angle
