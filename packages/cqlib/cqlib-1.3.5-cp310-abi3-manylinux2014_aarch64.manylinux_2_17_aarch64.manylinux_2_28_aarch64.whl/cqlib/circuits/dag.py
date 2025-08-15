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

"""Circuits as Directed Acyclic Graphs."""

# pylint: disable=E0611
from rustworkx import PyDiGraph, topological_sort, DAGHasCycle, NodeIndices
from cqlib.circuits.circuit import Circuit
from cqlib.circuits.instruction_data import InstructionData
from cqlib.circuits.parameter import Parameter
from cqlib.exceptions import CqlibError


def circuit_to_dag(circuit: Circuit) -> PyDiGraph:
    """
    Convert a quantum circuit into a Directed Acyclic Graph (DAG).

    Each operation in the circuit is added as a node in the DAG.
    Directed edges are created between nodes to maintain the operational
    dependencies determined by the qubits each operation acts upon.
    This ensures that operations are ordered correctly relative to the qubits they use.

    Args:
        circuit (Circuit): The quantum circuit to convert, containing a sequence of operations.

    Returns:
        nx.DiGraph: The directed acyclic graph representation of the circuit.
    """
    dag = PyDiGraph(check_cycle=True)
    qubit_last_nodes = {}
    node_ids = {}
    for op in circuit.instruction_sequence:
        if not isinstance(op, InstructionData):
            raise TypeError(f"{op} must be instance of InstructionData")
        node_id = dag.add_node(op)
        node_ids[op] = node_id
        for qubit in op.qubits:
            if qubit in qubit_last_nodes:
                last_node = qubit_last_nodes[qubit]
                dag.add_edge(node_ids[last_node], node_id, f'{last_node}-{op}')
            qubit_last_nodes[qubit] = op

    return dag


def dag_to_circuit(dag: PyDiGraph) -> Circuit:
    """
    Converts a Directed Acyclic Graph (DAG) back into a quantum circuit.
    The DAG is expected to have nodes representing quantum operations
    (InstructionData) and edges defining the order of these operations.

    Args:
        dag (nx.DiGraph): The DAG to convert, where nodes are operations
            and edges represent execution dependency.

    Returns:
        Circuit: A quantum circuit reconstructed from the DAG.
    """
    try:
        topological_order = topological_sort(dag)
    except DAGHasCycle as e:
        raise CqlibError("The provided graph must be acyclic to form a valid"
                         " quantum circuit.")  from e
    circuit = Circuit(0)

    for index in topological_order:
        node = dag.get_node_data(index)
        if not isinstance(node, InstructionData):
            raise CqlibError(f"{node} in the DAG must be instance of InstructionData")
        for qubit in node.qubits:
            if qubit not in circuit.qubits:
                circuit.add_qubit(qubit)
        for param in node.instruction.params:
            if isinstance(param, Parameter) and param not in circuit.parameters:
                circuit.add_parameter(param)
        circuit.append_instruction_data(node)

    return circuit


def topological_layers(graph: PyDiGraph) -> list[list[NodeIndices | int]]:
    """
    Perform topological sorting to decompose a directed acyclic graph
    (DAG) into layers of nodes.

    This function implements a Kahn's algorithm-based approach to determine
    the hierarchical layers of nodes in a DAG. Each layer contains nodes that
    can be processed simultaneously in dependency resolution scenarios.

    Args:
        graph (PyDiGraph): The input directed acyclic graph represented as
            a `PyDiGraph` object from the `rustworkx` library.

    Returns:
        list[list[NodeIndices]]: A list of lists where each inner list represents
            a layer of node IDs.
    """
    node_in_degree = {node: graph.in_degree(node) for node in graph.node_indices()}
    front_layer = [node_id for node_id, in_degree in node_in_degree.items() if in_degree == 0]

    while front_layer:
        yield front_layer
        next_layer = []
        for node_id in front_layer:
            for successor in graph.successor_indices(node_id):
                node_in_degree[successor] -= 1
                if node_in_degree[successor] == 0:
                    next_layer.append(successor)
        front_layer = next_layer
