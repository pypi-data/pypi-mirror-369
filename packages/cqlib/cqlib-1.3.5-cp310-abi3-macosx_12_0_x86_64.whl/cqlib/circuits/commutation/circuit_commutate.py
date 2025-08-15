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

""" Quantum circuit commutation checker """

from rustworkx.rustworkx import topological_sort

from cqlib.circuits.circuit import Circuit
from cqlib.circuits.instruction_data import InstructionData
from cqlib.circuits.dag import circuit_to_dag

from .commutation import check_commutation

from ._gates_commutations import gates_commutations


def circuit_commutator(
        circuit: Circuit,
        use_cache: bool = True,
        cache_commutations: dict = None
) -> list[tuple[InstructionData, InstructionData]]:
    """
    Check whether there is a commutation relationship between
    consecutive instructions in the circuit.

    Args:
        circuit(Circuit): Quantum circuit.
        use_cache(bool):
        cache_commutations(dict): .
    """
    if use_cache:
        if cache_commutations is None:
            cache_commutations = gates_commutations
    else:
        cache_commutations = gates_commutations
    dag = circuit_to_dag(circuit)
    data = []
    for node_idx in topological_sort(dag):
        node = dag.get_node_data(node_idx)
        for next_node in dag.successors(node_idx):
            if use_cache:
                res = query_commute(node, next_node, cache_commutations)
                if res is not None:
                    if res:
                        data.append((node, next_node))
                    continue
            if check_commutation(node, next_node):
                data.append((node, next_node))
    return data


def query_commute(
        gate_1: InstructionData,
        gate_2: InstructionData,
        cache_commutations: dict
) -> bool | None:
    """
    Determines if two quantum gates commute based on cached commutation information.

    Args:
        gate_1 (InstructionData): The first quantum gate as an InstructionData object.
        gate_2 (InstructionData): The second quantum gate as an InstructionData object.
        cache_commutations (dict): A dictionary used to cache commutation results between gates.
    """
    cache_commutation = {}
    if cache := cache_commutations.get(gate_1.instruction.name, None):
        if c := cache.get(gate_2.instruction.name, None):
            cache_commutation = c
    elif cache := cache_commutations.get(gate_2.instruction.name, None):
        if c := cache.get(gate_1.instruction.name, None):
            cache_commutation = c
            gate_1, gate_2 = gate_2, gate_1
    if not cache_commutation:
        return None

    if isinstance(cache_commutation, bool):
        return cache_commutation

    qubits = {q: index for index, q in enumerate(gate_2.qubits)}
    gate_1_qubits = (qubits.get(q) for q in gate_1.qubits)
    return cache_commutation.get(gate_1_qubits, None)
