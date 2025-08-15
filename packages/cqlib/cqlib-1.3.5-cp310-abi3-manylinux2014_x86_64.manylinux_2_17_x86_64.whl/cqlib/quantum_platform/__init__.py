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
Quantum Computing platforms.

This module provides an abstract and implementation for different quantum computing platforms,
 allowing for the execution and management of tasks across various quantum computing environments.

Classes:
    BasePlatform: A base class that provides the common interface and functionality for all
        quantum computing platforms. This includes basic operations such as authentication,
        job submission, and result retrieval.

    TianYanPlatform: A implementation of the BasePlatform tailored for the TianYan quantum
        computing quantum_platform. This class customizes the base functionalities with specific
         endpoints (URLs) and methods suited for the TianYan infrastructure.

    GuoDunPlatform: Similar to TianYanPlatform, this class is designed for the GuoDun quantum
        computing quantum_platform. It extends the BasePlatform with customizations specific
        to GuoDun's operational needs and technical specifications, including unique URLs and
        functions.

"""

from .base import BasePlatform, QuantumLanguage
from .tianyan import TianYanPlatform
from .guodun import GuoDunPlatform

__all__ = ['BasePlatform', 'TianYanPlatform', 'GuoDunPlatform', 'QuantumLanguage']
