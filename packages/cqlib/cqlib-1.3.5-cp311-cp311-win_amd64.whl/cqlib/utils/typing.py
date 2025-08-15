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
Typing utilities.

This module contains the following classes:
* :class:`ArrayLike`: Returns a ``Union`` of all array-like types, which
  includes any scalar or sequence that can be interpreted as a numpy array,
  including lists and tuples.
"""
import contextlib
import sys
from typing import Iterator

import numpy as np


class ArrayLikeMETA(type):
    """
    ArrayLike metaclass.
    """
    _normal_types = list, tuple, np.ndarray

    def __instancecheck__(cls, other):
        """ Check if an object is a `ArrayLike` instance. """
        return isinstance(other, cls._normal_types) or _is_torch(other)

    def __subclasscheck__(cls, other):
        """ Checks if a class is a subclass of ``ArrayLike``."""
        return issubclass(other, cls._normal_types) or _is_torch(other, subclass=True)


# pylint: disable=too-few-public-methods
class ArrayLike(metaclass=ArrayLikeMETA):
    """
    Returns a ``Union`` of all array-like types, which includes any scalar or sequence
    that can be interpreted as a numpy array, including lists and tuples.

    **Examples**

    >>> from cqlib.utils.typing import ArrayLike
    >>> isinstance([2, 6, 8], ArrayLike)
    True
    >>> isinstance(torch.tensor([1, 2, 3]), ArrayLike)
    True
    >>> issubclass(list, ArrayLike)
    True
    >>> isinstance(5, ArrayLike)
    False
    """

    def __len__(self) -> int:
        """Length of the array-like object."""
        return len(self)

    def __iter__(self) -> Iterator:
        """Iterate over array elements."""
        return iter(self)


def _is_torch(other, subclass=False):
    """ Check whether it is PyTorch tensor type. """
    if "torch" in sys.modules:
        with contextlib.suppress(ImportError):
            # pylint: disable=import-outside-toplevel
            from torch import Tensor as torchTensor
            check = issubclass if subclass else isinstance
            return check(other, torchTensor)
    return False
