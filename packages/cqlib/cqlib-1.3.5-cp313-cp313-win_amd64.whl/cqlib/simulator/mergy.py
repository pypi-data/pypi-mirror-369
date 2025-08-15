# This code is part of cqlib.
#
# (C) Copyright China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
This module provides functionality for simulating and fusing quantum gates.
"""

from collections import defaultdict
from collections.abc import Sequence

import networkx as nx
import numpy as np


class Gate:
    """
    A quantum gate.
    """

    def __init__(
            self,
            name: str,
            qubits: list[int] | None = None,
            theta: list[float] | None = None,
            mat: np.ndarray | None = None,
    ):
        """
        Initializes a Gate object.
        """
        self.name = name
        if qubits is None:
            self.qubits = []
        else:
            self.qubits = qubits
        if theta is None:
            self.theta = []
        else:
            self.theta = [float(i) for i in theta]
        if mat is None:
            self.mat = np.array([])
        else:
            self.mat = np.asarray(mat)

    def __repr__(self) -> str:
        return (f"\nname: {self.name}\nqubits: {self.qubits}\n"
                f"theta: {self.theta}\nmat: {self.mat}\n")


class FusionGate:
    """
    Represents a fused gate
    """

    def __init__(
            self,
            name: str,
            qubits: list[int] = None,
            idx: list = None
    ):
        """
        Initializes a FusionGate object.

        Args:
            name (str): The name of the gate.
            qubits (list[int] | None): The qubits that the gate acts on (default: None).
            idx (list | None): The indices of the gates being fused (default: None).
        """
        self.name = name
        if qubits is None:
            raise TypeError("Qubits is needed.")
        self.qubits = qubits
        if idx is None:
            self.idx = []
        else:
            self.idx = idx

    def __repr__(self) -> str:
        return f"\nname: {self.name}\nqubits: {self.qubits}\nidx: {self.idx}\n"


def to_dag(gates: Sequence[Gate]) -> nx.DiGraph:
    """
    Converts a sequence of gates into a directed acyclic graph (DAG).

    Args:
        gates (Sequence[Gate]): A sequence of Gate objects representing the quantum circuit.

    Returns:
        nx.DiGraph: A directed acyclic graph representing the gates and their dependencies.
    """
    dg = nx.DiGraph()
    pre_nodes = defaultdict(lambda: -1)

    for idx, gate in enumerate(gates):
        pre = [pre_nodes[q] for q in gate.qubits]
        dg.add_node(idx, gate=FusionGate(gate.name, gate.qubits.copy(), [idx]))
        for p in pre:
            if p != -1:
                dg.add_edge(p, idx)
        predecessors = list(dg.predecessors(idx))

        if len(predecessors) == 1:
            gate1 = dg.nodes[idx]["gate"]
            gate2 = dg.nodes[predecessors[0]]["gate"]
            if set(gate1.qubits) & set(gate2.qubits) == set(gate1.qubits):
                dg.nodes[predecessors[0]]["gate"].idx += gate1.idx
                dg.nodes[predecessors[0]]["gate"].name = "fgate"
                dg.remove_node(idx)
        else:
            gate1 = dg.nodes[idx]["gate"]
            for predecessor in predecessors:
                gate2 = dg.nodes[predecessor]["gate"]
                if set(gate1.qubits) & set(gate2.qubits) == set(gate2.qubits):
                    if all(pre_nodes[q] == predecessor for q in gate2.qubits):
                        dg.nodes[idx]["gate"].idx += gate2.idx
                        dg.nodes[idx]["gate"].name = "fgate"
                        for j in dg.predecessors(predecessor):
                            dg.add_edge(j, idx)
                        dg.remove_node(predecessor)

        if dg.has_node(idx):
            for q in gate.qubits:
                pre_nodes[q] = idx

    return dg


class CostBasedFusion:
    """
    Implements a cost-based method to fuse quantum gates, aiming to reduce computational cost
    by estimating the fusion cost and aggregating gates with the lowest cost.
    """

    def __init__(self, cost_factor: float = 1.8):
        """ Initializes the CostBasedFusion object with a cost factor. """
        self.cost_factor = cost_factor
        self.costs = [-1] * 64

    def add_fusion_qubits(self, fusion_qubits: set, gate: Gate) -> None:
        """
        Adds the qubits from the given gate to the set of fusion qubits.

        Args:
            fusion_qubits (set): The set of qubits involved in the fusion.
            gate (Gate): The gate whose qubits are being added.
        """
        for qubit in gate.qubits:
            if qubit not in fusion_qubits:
                fusion_qubits.add(qubit)

    def estimate_cost(self, fusion_gates: list, from_idx: int, until_idx: int) -> float:
        """
        Estimates the fusion cost for a sequence of gates based on the number of qubits involved.

        Args:
            fusion_gates (list[Gate]): The list of gates to be fused.
            from_idx (int): The starting index of the fusion range.
            until_idx (int): The ending index of the fusion range.

        Returns:
            float: The estimated cost of the fusion.
        """
        fusion_qubits = set()
        for i in range(from_idx, until_idx + 1):
            self.add_fusion_qubits(fusion_qubits, fusion_gates[i])
        configured_cost = self.costs[len(fusion_qubits) - 1]
        if configured_cost > 0:
            return configured_cost

        return np.power(self.cost_factor, max(len(fusion_qubits) - 1, 1))

    def aggregate_gates(
            self,
            fusion_gates: list,
            fusion_start: int,
            fusion_end: int,
            max_fused_qubits: int,
    ) -> list:
        """
        Aggregates gates within the specified range based on the cost estimation, and returns
        a list of fused gates.

        Args:
            fusion_gates (list[Gate]): The list of gates to be fused.
            fusion_start (int): The starting index of the fusion.
            fusion_end (int): The ending index of the fusion.
            max_fused_qubits (int): The maximum number of qubits allowed in a single fusion.

        Returns:
            list: A list of fused gates.
        """
        fusions = []
        fusion_to = [fusion_start]
        costs = [np.power(
            self.cost_factor,
            max(len(fusion_gates[fusion_start].qubits) - 1, 1),
        )]

        for i in range(fusion_start + 1, fusion_end):
            fusion_to.append(i)
            costs.append(costs[i - fusion_start - 1] + self.cost_factor)
            for num_fusion in range(2, max_fused_qubits + 1):
                fusion_qubits = set()
                self.add_fusion_qubits(fusion_qubits, fusion_gates[i])
                for j in range(i - 1, fusion_start - 1, -1):
                    self.add_fusion_qubits(fusion_qubits, fusion_gates[j])

                    if len(fusion_qubits) > num_fusion:
                        break

                    estimated_cost = self.estimate_cost(fusion_gates, j, i) + (
                        0.0 if j <= fusion_start else costs[j - 1 - fusion_start]
                    )
                    if estimated_cost <= costs[i - fusion_start]:
                        costs[i - fusion_start] = estimated_cost
                        fusion_to[i - fusion_start] = j

        i = fusion_end - 1
        while i >= fusion_start:
            to = fusion_to[i - fusion_start]
            gate = fusion_gates[to]
            for j in range(to + 1, i + 1):
                gate.idx += fusion_gates[j].idx
                gate.qubits += fusion_gates[j].qubits
                gate.name = "fgate"
            gate.qubits = set(gate.qubits)
            fusions.append(gate)
            i = to - 1
        fusions = fusions[::-1]
        # return fusions
        return self.convert(fusions)

    @staticmethod
    def convert(fusions: list):
        dg = nx.DiGraph()
        pre_nodes = defaultdict(lambda: -1)
        for idx, gate in enumerate(fusions):
            pre = [pre_nodes[q] for q in gate.qubits]
            dg.add_node(idx, gate=gate)
            for p in pre:
                if p == -1:
                    continue
                dg.add_edge(p, idx)
            predecessors = list(dg.predecessors(idx))
            if len(predecessors) == 1:
                gate1 = dg.nodes[idx]["gate"]
                gate2 = dg.nodes[predecessors[0]]["gate"]
                if gate1.qubits & gate2.qubits == gate1.qubits:
                    dg.nodes[predecessors[0]]["gate"].idx += gate1.idx
                    dg.nodes[predecessors[0]]["gate"].name = "fgate"
                    dg.remove_node(idx)
            else:
                gate1 = dg.nodes[idx]["gate"]
                for predecessor in predecessors:
                    gate2 = dg.nodes[predecessor]["gate"]
                    if gate1.qubits & gate2.qubits == gate2.qubits:
                        if all([pre_nodes[q] == predecessor for q in gate2.qubits]):
                            dg.nodes[idx]["gate"].idx += gate2.idx
                            dg.nodes[idx]["gate"].name = "fgate"
                            for j in dg.predecessors(predecessor):
                                dg.add_edge(j, idx)
                            dg.remove_node(predecessor)

            if dg.has_node(idx):
                for q in gate.qubits:
                    pre_nodes[q] = idx

        fusions_gate = []
        for node in dg.nodes:
            fusions_gate.append(dg.nodes[node]["gate"])
            fusions_gate[-1].idx.sort()
        return fusions_gate


def get_mat(
        gates: list[Gate],
        fusion: FusionGate,
        qnum: int,
        qmap: dict
) -> np.ndarray:
    """
    Generates the matrix for a given gate and maps it to the appropriate qubits.

    Args:
        gates (list[Gate]): The quantum gate list.
        qnum (int): The total number of qubits.
        qmap (dict): A dictionary mapping the qubit indices to the correct position.

    Returns:
        np.ndarray: The matrix representation of the gate applied to the correct qubits.
    """
    shape = [2 ** qnum] + [2 for _ in range(qnum)]
    mat = np.eye(2 ** qnum).reshape(shape)
    for i in fusion.idx:
        op = gates[i]
        qubits = [qmap[q] for q in op.qubits]
        subscripts = (
                [0]
                + [qubit + 1 for qubit in qubits]
                + [
                    i
                    for i in range(1, qnum + 1)
                    if i not in {qubit + 1 for qubit in qubits}
                ]
        )
        mat = np.reshape(np.transpose(mat, subscripts), (2 ** qnum, 2 ** len(qubits), -1))
        mat = np.matmul(np.reshape(op.mat, (2 ** len(qubits), -1)), mat)
        mat = np.transpose(
            np.reshape(mat, shape),
            _inv_subscripts(subscripts),
        )
    mat = mat.reshape(2 ** qnum, -1).T.copy()
    return mat


def _inv_subscripts(subscripts: list[int]) -> list[int]:
    inv = [0] * len(subscripts)
    for i, sub in enumerate(subscripts):
        inv[sub] = i
    return inv


def fusion_to_gate(gates: list, fusion: FusionGate) -> Gate:
    """
    Converts a fusion gate back into a regular gate, creating a matrix that represents
    the entire fusion operation.

    Args:
        gates (list[Gate]): The list of original gates.
        fusion (FusionGate): The fusion gate to convert.

    Returns:
        Gate: A new Gate object representing the fused operation.
    """
    if fusion.name == "fgate":
        qubits = list(fusion.qubits)
        qnum = len(qubits)
        qubits.sort()
        qmap = {}
        for i, v in enumerate(qubits):
            qmap[v] = i
        mat = get_mat(gates, fusion, qnum, qmap)
        return Gate(fusion.name, qubits, theta=[], mat=mat)
    return gates[fusion.idx[0]]


def merge_gate(ori_gates: list[Gate], max_qubit: int) -> list[Gate]:
    """
    Merges the given sequence of gates into a more efficient representation by fusing gates
    acting on adjacent qubits, up to a specified limit of qubits.

    Args:
        ori_gates (list[Gate]): The list of original gates.
        max_qubit (int): The maximum number of qubits allowed in a fused gate.

    Returns:
        list[Gate]: A new list of gates, some of which may be fused.
    """
    if max_qubit == 1:
        return ori_gates
    dg = to_dag(ori_gates)
    fusion_gates = []

    for node in dg.nodes:
        fusion_gates.append(dg.nodes[node]["gate"])

    fusion_method = CostBasedFusion()
    fusion_gates = fusion_method.aggregate_gates(
        fusion_gates, 0, len(fusion_gates), max_qubit
    )
    new_gates = []
    for fusion in fusion_gates:
        new_gates.append(fusion_to_gate(ori_gates, fusion))

    return new_gates
