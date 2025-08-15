# This code is part of cqlib.
#
# (C) Copyright China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics 2025.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Quantum gate matrix generators for simulation.

This module provides matrix representations of common single-qubit rotation gates
(RX, RY, RZ) and their controlled versions (CRX, CRY, CRZ) using a specified
computational backend (TorchBackend).
"""

import numpy as np

from cqlib.circuits.gates import X, Y, Z

from .torch_backend import TorchBackend

x_mat = np.asarray(X())
y_mat = np.asarray(Y())
z_mat = np.asarray(Z())


def rx_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of RX gate (rotation around X-axis).
    """
    i = backend.eye(2)
    x = backend.as_tensor(x_mat)
    theta = backend.as_tensor(theta)
    num = backend.numel(theta)
    if num != 1:
        raise ValueError(
            f"The number of parameters for `RX` gate can only be 1 but got `{num}`."
        )
    return backend.cos(theta / 2.0) * i - backend.i() * backend.sin(theta / 2.0) * x


def ry_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of RY gate (rotation around Y-axis).
    """
    i = backend.eye(2)
    y = backend.as_tensor(y_mat)
    theta = backend.as_tensor(theta)
    num = backend.numel(theta)
    if num != 1:
        raise ValueError(
            f"The number of parameters for `RY` gate can only be 1 but got `{num}`."
        )
    return backend.cos(theta / 2.0) * i - backend.i() * backend.sin(theta / 2.0) * y


def rz_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of RZ gate (rotation around Z-axis).
    """
    i = backend.eye(2)
    z = backend.as_tensor(z_mat)
    theta = backend.as_tensor(theta)
    num = backend.numel(theta)
    if num != 1:
        raise ValueError(
            f"The number of parameters for `RZ` gate can only be 1 but got `{num}`."
        )
    return backend.cos(theta / 2.0) * i - backend.i() * backend.sin(theta / 2.0) * z


def xy_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of the XY gate using hstack/vstack.

    Args:
        theta: Rotation angle (in radians)
        backend: Backend support (e.g., TorchBackend)

    Returns:
        Tensor representation of the XY gate
    """
    theta = backend.as_tensor(theta)
    num = backend.numel(theta)
    if num != 1:
        raise ValueError(
            f"XY gate requires exactly 1 parameter, got {num}."
        )

    # Compute exp(iθ) and exp(-iθ)
    exp_i_theta = backend.exp(backend.i() * theta)
    exp_neg_i_theta = backend.exp(-backend.i() * theta)

    matrix = -backend.i() * backend.vstack([
        backend.hstack([backend.zeros(1), exp_neg_i_theta]),
        backend.hstack([exp_i_theta, backend.zeros(1)])
    ])

    return matrix


def xy2p_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of the XY2P gate.

    Args:
        theta: Rotation angle (in radians)
        backend: Backend support (e.g., TorchBackend)

    Returns:
        torch.Tensor: Matrix representation of the XY2P gate
    """
    # Convert theta to tensor and validate
    theta = backend.as_tensor(theta)
    if backend.numel(theta) != 1:
        raise ValueError("XY2P gate requires exactly 1 parameter.")

    i = backend.i()  # 1j
    neg_i = backend.mul(-1, i)  # -1j
    exp_i_theta = backend.exp(i * theta)
    exp_neg_i_theta = backend.exp(-i * theta)
    sqrt2_inv = 1 / backend.sqrt(backend.as_tensor(2.0))  # 1/sqrt(2)

    one = backend.eye(1)

    return backend.mul(sqrt2_inv, backend.vstack([
        backend.hstack([one, backend.mul(neg_i, exp_neg_i_theta).reshape(1, 1)]),
        backend.hstack([backend.mul(neg_i, exp_i_theta).reshape(1, 1), one])
    ]))


def xy2m_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of the XY2M gate.

    Args:
        theta: Rotation angle (in radians)
        backend: Backend support (e.g., TorchBackend)

    Returns:
        torch.Tensor: Matrix representation of the XY2M gate
    """
    # Convert theta to tensor and validate
    theta = backend.as_tensor(theta)
    if backend.numel(theta) != 1:
        raise ValueError("XY2P gate requires exactly 1 parameter.")

    # Compute required components
    i = backend.i()  # Imaginary unit 1j
    exp_i_theta = backend.exp(i * theta)
    exp_neg_i_theta = backend.exp(-i * theta)
    sqrt2_inv = 1 / backend.sqrt(backend.as_tensor(2.0))  # 1/sqrt(2)

    # Create matrix elements
    one = backend.eye(1)  # Create [[1]] and then reshape if needed

    # Create complex elements as 2D tensors
    top_right = backend.mul(i, exp_neg_i_theta).reshape(1, 1)  # [[i*exp(-iθ)]]
    bottom_left = backend.mul(i, exp_i_theta).reshape(1, 1)

    # Construct matrix rows
    row1 = backend.hstack([one, top_right])
    row2 = backend.hstack([bottom_left, one])

    return backend.mul(sqrt2_inv, backend.vstack([row1, row2]))


def rxy_mat(phi, theta, backend: TorchBackend):
    """
    Generate the matrix representation of RXY gate
    """
    i = backend.eye(2)
    x = backend.as_tensor(x_mat)
    y = backend.as_tensor(y_mat)
    phi = backend.as_tensor(phi)
    theta = backend.as_tensor(theta)
    num_theta = backend.numel(theta)
    num_phi = backend.numel(phi)
    if num_theta != 1 or num_phi != 1:
        raise ValueError(
            f"The number of parameters for `RXY` gate must be 2 (theta and phi)"
            f" but got {num_theta} and {num_phi}."
        )
    cos_term = backend.cos(theta / 2.0) * i
    sin_term = (-backend.i() * backend.sin(theta / 2.0) *
                (backend.cos(phi) * x + backend.sin(phi) * y))
    return cos_term + sin_term


def u_mat(theta, phi, lam, backend: TorchBackend):
    """
    Generate the matrix representation of the U gate.

    Args:
        theta: Rotation angle (in radians)
        phi: First phase angle (in radians)
        lam: Second phase angle (in radians)
        backend: The backend used for tensor operations (e.g., TorchBackend)

    Returns:
        Tensor representation of the U gate
    """
    # Convert inputs to tensors and validate
    theta = backend.as_tensor(theta)
    phi = backend.as_tensor(phi)
    lam = backend.as_tensor(lam)

    if (backend.numel(theta) != 1 or
            backend.numel(phi) != 1 or
            backend.numel(lam) != 1):
        raise ValueError("U gate requires exactly 1 value for each parameter.")

    # Compute trigonometric terms
    half_theta = theta / 2
    cos = backend.cos(half_theta)
    sin = backend.sin(half_theta)
    i = backend.i()

    # Build matrix using hstack/vstack
    row1 = backend.hstack([cos, -backend.exp(i * lam) * sin])
    row2 = backend.hstack([backend.exp(i * phi) * sin, backend.exp(i * (phi + lam)) * cos])
    matrix = backend.vstack([row1, row2])

    return matrix


def crx_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of controlled-RX gate.
    """
    rx = rx_mat(theta, backend)
    return _cr_mat(backend, rx)


def cry_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of controlled-RY gate.
    """
    ry = ry_mat(theta, backend)
    return _cr_mat(backend, ry)


def crz_mat(theta, backend: TorchBackend):
    """
    Generate the matrix representation of controlled-RZ gate.
    """
    rz = rz_mat(theta, backend)
    return _cr_mat(backend, rz)


def _cr_mat(backend: TorchBackend, mat):
    """
    Internal function: Construct matrix for controlled rotation gates.
    """
    i_2x2 = backend.eye(2)
    zero_2x2 = backend.zeros((2, 2))

    crz = backend.vstack([
        backend.hstack([i_2x2, zero_2x2]),
        backend.hstack([zero_2x2, mat])
    ])
    return crz
