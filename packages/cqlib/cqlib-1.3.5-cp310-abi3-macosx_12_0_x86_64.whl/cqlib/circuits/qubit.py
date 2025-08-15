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

"""Quantum bit."""

from __future__ import annotations

import weakref

from .bit import Bit


class Qubit(Bit):
    """Quantum bit."""
    __slots__ = ["__weakref__"]
    _cache = weakref.WeakValueDictionary[int, 'Qubit']()

    def __new__(cls, index: int) -> Qubit:
        """
        Create a new Qubit instance or return an existing one from
        the cache based on the given index.

        Args:
            index: The logical index of the qubit which must be non-negative.

        Returns:
            An instance of Qubit.
        """
        if index < 0:
            raise ValueError("Qubit index must be non-negative.")

        inst = cls._cache.get(index)
        if inst is None:
            inst = super().__new__(cls)
            inst._index = index
            inst._hash = None
            inst._initialized = True
            cls._cache[index] = inst
        return inst

    def __str__(self):
        return f'Q{self.index}'
