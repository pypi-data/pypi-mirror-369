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

""" quantum bit base class"""

from __future__ import annotations


class Bit:
    """Quantum bit."""
    __slots__ = ["_index", '_initialized', '_hash']

    def __init__(self, index: int):
        """
        Initialize a new Qubit instance.

        Args:
            index: logical index of the qubit
        """
        if index < 0:
            raise ValueError("Index must be non-negative.")
        if not hasattr(self, '_initialized'):
            self._index = index
            self._hash = None
            self._initialized = True

    @property
    def index(self) -> int:
        """Returns the logical index of the qubit."""
        return self._index

    def __repr__(self):
        return f"{self.__class__.__name__}({self.index})"

    def __str__(self):
        return f'Bit{self.index}'

    def __copy__(self):
        """
        Returns a reference to the same qubit instance since qubits
        should be unique.
        """
        return self

    def __deepcopy__(self, memo=None):
        return self

    def __eq__(self, other: Bit) -> bool:
        """Check equality with another qubit based on the index."""
        return (isinstance(other, self.__class__) and
                self.index == other.index)

    def __hash__(self) -> int:
        """
        Return the hash based on the qubit's index, used for collections
        that depend on hashable items.
        """
        if self._hash is None:
            self._hash = hash(f"{self.__class__.__name__}({self._index})")
        return self._hash
