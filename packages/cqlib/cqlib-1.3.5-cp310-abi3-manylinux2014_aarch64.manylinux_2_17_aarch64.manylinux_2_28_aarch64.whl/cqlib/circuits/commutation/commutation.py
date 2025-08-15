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

""" Check commutation """

from functools import lru_cache

import numpy as np

from cqlib.circuits.qubit import Qubit
from cqlib.circuits.instruction import Instruction
from cqlib.circuits.instruction_data import InstructionData


@lru_cache()
def _identity_op(num_qubits):
    """Cached identity matrix"""
    return np.eye(2 ** num_qubits)


def check_commutation(
        op_1: InstructionData,
        op_2: InstructionData,
) -> bool:
    """
    Check commutation

    Args:
        op_1 (InstructionData): instruction 1
        op_2 (InstructionData): instruction 2
    """
    qubits_1 = op_1.qubits
    qubits_2 = op_2.qubits

    if set(qubits_1).isdisjoint(qubits_2):
        return True

    if not hasattr(op_1.instruction, '__array__') or not hasattr(op_2.instruction, '__array__'):
        return False

    if qubits_1 == qubits_2:
        return commute(op_1.instruction, op_2.instruction)

    qubits = {qubit: i for i, qubit in enumerate(qubits_1)}
    num_qubits = len(qubits)
    for q in qubits_2:
        if q not in qubits:
            qubits[q] = num_qubits
            num_qubits += 1

    data_1 = _to_matrix(op_1, num_qubits=num_qubits, qubits=qubits)
    data_2 = _to_matrix(op_2, num_qubits=num_qubits, qubits=qubits)

    return commute(data_1, data_2)


def _to_matrix(instr: InstructionData, qubits: dict[Qubit, int], num_qubits: int):
    """
    Convert a quantum instruction into its corresponding unitary matrix representation.

    Args:
        instr(InstructionData): The quantum instruction data, containing both the
            instruction itself and the qubits it affects.
        qubits(dict[Qubit, int]): A mapping from Qubit objects to their corresponding
            index positions in the quantum register.
        num_qubits(int): The total number of qubits in the quantum circuit, which
            determines the size of the unitary matrix.
    """
    if (not hasattr(instr.instruction, 'is_supported_by_qcis')
            or instr.instruction.is_supported_by_qcis):
        gates = [instr]
    else:
        gates = instr.instruction.to_qcis(instr.qubits)

    mat = np.eye(2 ** num_qubits, dtype=np.complex128)
    for gate in gates[::-1]:
        qs = [qubits[q] for q in gate.qubits]
        gate_matrix = _to_ndarray(gate.instruction)
        exp_mat = _expand_gate(gate_matrix, qubits=qs, num_qubits=num_qubits)
        mat = exp_mat @ mat

    return mat


def _expand_gate(gate_matrix: np.ndarray, qubits: list[int], num_qubits: int):
    """
    Expands a quantum gate matrix to the full dimension of the quantum register.

    Args:
        gate_matrix(np.ndarray): The matrix representation of the quantum gate. This
            should be a 2x2 matrix for single-qubit gates or a 4x4 matrix for two-qubit gates.
        qubits(list[int]): A list of integers representing the indices of the qubits
            the gate acts upon. This list can contain one or two elements.
        num_qubits(int): The total number of qubits.
    """
    qubits_len = len(qubits)
    if qubits_len == 1:
        q = qubits[0]
        mat = np.eye(2 ** q)
        mat = np.kron(mat, gate_matrix)
        mat = np.kron(mat, np.eye(2 ** (num_qubits - 1 - q)))
    elif qubits_len == 2:
        if not np.array_equal(gate_matrix[0:2, 0:2], np.eye(2)):
            raise ValueError("Only supports control gates")

        c, t = qubits
        mat1 = np.eye(2 ** c)
        mat1 = np.kron(mat1, np.diag([1, 0]))
        mat1 = np.kron(mat1, np.eye(2 ** (num_qubits - 1 - c)))

        if c < t:
            mat2 = np.eye(2 ** c)
            mat2 = np.kron(mat2, np.diag([0, 1]))
            mat2 = np.kron(mat2, np.eye(2 ** (t - 1 - c)))
            mat2 = np.kron(mat2, gate_matrix[2:4, 2:4])
            mat2 = np.kron(mat2, np.eye(2 ** (num_qubits - 1 - t)))
        else:
            mat2 = np.eye(2 ** t)
            mat2 = np.kron(mat2, gate_matrix[2:4, 2:4])
            mat2 = np.kron(mat2, np.eye(2 ** (c - 1 - t)))
            mat2 = np.kron(mat2, np.diag([0, 1]))
            mat2 = np.kron(mat2, np.eye(2 ** (num_qubits - 1 - c)))
        mat = mat1 + mat2
    else:
        raise ValueError("Only supports two bit operation gates")
    return mat


def commute(
        instr_1: Instruction | np.ndarray | list[list],
        instr_2: Instruction | np.ndarray | list[list],
) -> bool:
    """
    Determine whether two quantum gates or matrices commute.

    Args:
        instr_1(Instruction | np.ndarray | list[list]): The first matrix, quantum gate, or
            list representation of the matrix.
        instr_2(Instruction | np.ndarray | list[list]): The second matrix, quantum gate, or
            list representation of the matrix.
    """
    data_1 = _to_ndarray(instr_1)
    data_2 = _to_ndarray(instr_2)

    if (data_1.shape != data_2.shape or len(data_1.shape) != 2
            or data_1.shape[0] != data_1.shape[1]):
        return False

    return np.allclose(data_1 @ data_2, data_2 @ data_1)


def _to_ndarray(data: Instruction | np.ndarray | list[list]) -> np.ndarray:
    """
    Converts various types of input data into a NumPy array.

    Args:
        data (Instruction | np.ndarray | list[list]): The input data to convert.
    """
    if isinstance(data, np.ndarray):
        return data
    if isinstance(data, Instruction):
        if hasattr(data, '__array__'):
            return np.array(data)
    elif isinstance(data, list):
        return np.array(data)

    raise ValueError(f"Unsupported data type: {data}")
