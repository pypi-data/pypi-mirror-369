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
PyTorch Backend for Quantum Circuit Simulation
"""
try:
    import torch
except ImportError:
    pass

# pylint: disable=too-many-public-methods
class TorchBackend:
    """
    PyTorch Backend
    """
    def __init__(self, dtype: type | None = None, device="cpu") -> None:
        """Initialize the PyTorch backend.

        Args:
            dtype: Data type for tensors (default: torch.complex128)
            device: Device for computation ('cpu' or 'cuda')
        """
        if dtype is None:
            dtype = torch.complex128
        self.dtype = dtype
        if not device:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if isinstance(device, str):
            device = torch.device(device)
        self.device = device

    def as_tensor(self, tensor):
        """Convert input to PyTorch tensor with specified dtype and device.

        Args:
            tensor: Input data to convert

        Returns:
            torch.Tensor: Converted tensor
        """
        return torch.as_tensor(tensor, dtype=self.dtype, device=self.device)

    def zeros(self, shape):
        """Create tensor filled with zeros.

        Args:
            shape: Shape of the output tensor

        Returns:
            torch.Tensor: Zero-filled tensor
        """
        return torch.zeros(shape, dtype=self.dtype, device=self.device)

    def reshape(self, tensor, shape):
        """Reshape tensor to specified shape.

        Args:
            tensor: Input tensor
            shape: Target shape

        Returns:
            torch.Tensor: Reshaped tensor
        """
        tensor = self.as_tensor(tensor)
        return torch.reshape(tensor, shape)

    def matmul(self, tensor1, tensor2):
        """Matrix multiplication of two tensors.

        Args:
            tensor1: First input tensor
            tensor2: Second input tensor

        Returns:
            torch.Tensor: Result of matrix multiplication
        """
        tensor1 = self.as_tensor(tensor1)
        tensor2 = self.as_tensor(tensor2)
        return torch.matmul(tensor1, tensor2)

    def vstack(self, tensors):
        """Stack tensors vertically (row-wise).

        Args:
            tensors: Sequence of tensors to stack

        Returns:
            torch.Tensor: Vertically stacked tensor
        """
        tensors = [self.as_tensor(tensor) for tensor in tensors]
        return torch.vstack(tensors)

    def hstack(self, tensors):
        """ Stack tensors horizontally (column-wise). """
        tensors = [self.as_tensor(tensor) for tensor in tensors]
        return torch.hstack(tensors)

    def ravel(self, tensor):
        """ Flatten a tensor into 1-dimensional array."""
        tensor = self.as_tensor(tensor)
        return torch.ravel(tensor)

    def conj(self, tensor):
        """ Compute the complex conjugate of a tensor. """
        tensor = self.as_tensor(tensor)
        return torch.conj(tensor)

    def real(self, tensor):
        """ Get the real part of a complex tensor. """
        tensor = self.as_tensor(tensor)
        return torch.real(tensor)

    def sin(self, tensor):
        """ Compute sine of tensor elements. """
        tensor = self.as_tensor(tensor)
        return torch.sin(tensor)

    def cos(self, tensor):
        """ Compute cosine of tensor elements. """
        tensor = self.as_tensor(tensor)
        return torch.cos(tensor)

    def exp(self, tensor):
        """ Compute exponential of tensor elements. """
        tensor = self.as_tensor(tensor)
        return torch.exp(tensor)

    def sqrt(self, tensor):
        """ Compute square root of tensor elements. """
        tensor = self.as_tensor(tensor)
        return torch.sqrt(tensor)

    def add(self, tensor, other):
        """ Add two tensors element-wise. """
        tensor = self.as_tensor(tensor)
        other = self.as_tensor(other)
        return torch.add(tensor, other)

    def mul(self, tensor, other):
        """ Multiply two tensors element-wise. """
        tensor = self.as_tensor(tensor)
        other = self.as_tensor(other)
        return torch.mul(tensor, other)

    def i(self):
        """ Get the imaginary unit (1j) as a tensor. """
        return torch.tensor(1j, dtype=self.dtype, device=self.device)

    def permute(self, tensor, axes=None):
        """ Permute tensor dimensions according to given axes. """
        tensor = self.as_tensor(tensor)
        return torch.permute(tensor, axes)

    def sum(self, tensor, axis=None):
        """ Sum tensor elements over given axis. """
        tensor = self.as_tensor(tensor)
        return torch.sum(tensor, axis)

    def to_numpy(self, tensor):
        """ Convert tensor to NumPy array. """
        tensor = self.as_tensor(tensor)
        return tensor.detach().cpu().numpy()

    def einsum(self, subscripts: str, *tensors):
        """ Einstein summation convention. """
        tensors = [self.as_tensor(tensor) for tensor in tensors]
        return torch.einsum(subscripts, *tensors)

    def kron(self, tensor1, tensor2):
        """ Compute Kronecker product of two tensors. """
        tensor1 = self.as_tensor(tensor1)
        tensor2 = self.as_tensor(tensor2)
        return torch.kron(tensor1, tensor2)

    def eye(self, n: int):
        """Create identity matrix of size N×N.

        Args:
            n: Size of the identity matrix

        Returns:
            torch.Tensor: Identity matrix
        """
        return torch.eye(n, dtype=self.dtype, device=self.device)

    def numel(self, tensor) -> int:
        """Get total number of elements in tensor.

        Args:
            tensor: Input tensor

        Returns:
            int: Total number of elements
        """
        tensor = self.as_tensor(tensor)
        return tensor.numel()
