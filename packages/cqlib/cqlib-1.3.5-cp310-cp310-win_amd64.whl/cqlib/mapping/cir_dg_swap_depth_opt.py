# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 20:13:14 2022

@author: zhoux

This module provides a modified cir_dg (DGSwap) which can be used for optimizing 
the depth of a circuit output by a QCT algorithm.

It accepts CNOT, SWAP and arbitrary single-qubit gate as nodes and the weight 
of the incoming edge of a node represents the latency of the corresponding node.

The DGSwap has a root node connecting all nodes (gates) in the front layer.
"""
import networkx as nx
import numpy as np
from .cir_dg import DG

gate_depth = {'cx': 1, 'h': 1, 't': 1, 'x': 1, 'y': 1, 'z': 1, 's': 1, 'rx': 1, 'ry': 1,
              'rz': 1, 'u3': 1, 'tdg': 1, 'swap': 3, 'p': 1, 'u2': 1, 'u1': 1, 'u': 1,
              'cz': 1, 'sdg': 1, 'sx': 1, 'sxdg': 1, 'x2p': 1,
              'y2m': 1, 'x2m': 1, 'xy2m': 1, 'xy2p': 1,
              'y2p': 1}


def swap_qubits_(qubits, swap_qubits):
    qubits_new = []
    for q in qubits:
        if q == swap_qubits[0]:
            qubits_new.append(swap_qubits[1])
        else:
            if q == swap_qubits[1]:
                qubits_new.append(swap_qubits[0])
            else:
                qubits_new.append(q)
    return qubits_new


def hybridization(dg_swap1, dg_swap2, dg_ori, prob1=0.5):
    '''
    We choose the first prob1% gates in dg_swap1 and the last (1-prob1)% gates
    in dg_swap2.
    '''
    from copy import deepcopy
    dg_swap_new = deepcopy(dg_ori)
    node_thre = int((len(dg_swap1.nodes) - len(dg_swap2.swap_nodes)) * prob1)
    exchange1, exchange2 = dg_swap1.exchange_log, dg_swap2.exchange_log
    for node1, node2 in exchange1:
        node_max = min(node1, node2)
        if (node1, node2) in dg_swap_new.exchange_log or (node2, node1) in dg_swap_new.exchange_log:
            continue
        if node_max <= node_thre: flag = dg_swap_new.exchange(node1, node2)
    for node1, node2 in exchange2:
        if (node1, node2) in dg_swap_new.exchange_log or (node2, node1) in dg_swap_new.exchange_log:
            continue
        node_max = max(node1, node2)
        if node_max > node_thre: flag = dg_swap_new.exchange(node1, node2)
    return dg_swap_new


def hybridization2(dg_swap1, dg_swap2, dg_ori, prob1=0.5):
    '''
    For each exchange, we randomly accept (prob1%) in dg_swap1 or 
    [(1-prob1)%] that in dg_swap2.
    '''
    from copy import deepcopy
    dg_swap_new = deepcopy(dg_ori)
    exchange1, exchange2 = dg_swap1.exchange_log, dg_swap2.exchange_log
    for node1, node2 in exchange1:
        if np.random.rand() < prob1:
            if (node1, node2) in dg_swap_new.exchange_log or (node2, node1) in dg_swap_new.exchange_log:
                continue
            dg_swap_new.exchange(node1, node2)
    for node1, node2 in exchange2:
        if np.random.rand() < (1 - prob1):
            if (node1, node2) in dg_swap_new.exchange_log or (node2, node1) in dg_swap_new.exchange_log:
                continue
            dg_swap_new.exchange(node1, node2)
    return dg_swap_new


def hybridization3(dg_swap1, dg_swap2, dg_ori):
    '''
    For each exchange, we accept all exchanges in dg_swap1 and dg_swap2.
    '''
    from copy import deepcopy
    dg_swap_new = deepcopy(dg_ori)
    exchange1, exchange2 = dg_swap1.exchange_log.copy(), dg_swap2.exchange_log.copy()
    exchange = []
    while len(exchange1) > 0 and len(exchange2) > 0:
        if np.random.rand() < 0.5:
            exchange.append(exchange1.pop(0))
        else:
            exchange.append(exchange2.pop(0))
    if len(exchange1) > 0:
        exchange.extend(exchange1)
    if len(exchange2) > 0:
        exchange.extend(exchange2)
    for node1, node2 in exchange:
        if (node1, node2) in dg_swap_new.exchange_log or (node2, node1) in dg_swap_new.exchange_log:
            continue
        dg_swap_new.exchange(node1, node2)
    return dg_swap_new


def hybridization4(dg_swap1, dg_swap2, dg_ori):
    '''
    For each exchange, we use dg_swap1 and then try to exchange using dg_swap2
    one-by-one and accept only that reducing depth.
    '''
    from copy import deepcopy
    dg_swap_new = deepcopy(dg_swap1)
    exchange2 = dg_swap2.exchange_log.copy()
    depth_ori = dg_swap_new.depth
    for node1, node2 in exchange2:
        if (node1, node2) in dg_swap_new.exchange_log or (node2, node1) in dg_swap_new.exchange_log:
            continue
        flag = dg_swap_new.exchange(node1, node2)
        if flag:
            depth_new = dg_swap_new.depth
            if depth_new < depth_ori:
                # accept
                depth_ori = depth_new
            else:
                if depth_new == depth_ori:
                    # accept with ??% probability
                    if np.random.rand() < 1: continue
                # recover
                dg_swap_new.exchange(node1, node2)
                dg_swap_new.exchange_log.pop(-1)
                dg_swap_new.exchange_log.pop(-1)

    return dg_swap_new


class DGSwap(DG):
    def __init__(self, ag, cost_func='depth'):
        super().__init__()
        # add root node
        self.add_node(self.node_count)
        self.root = self.node_count
        self.node_count += 1
        self.nodes[self.root]['gates'] = []
        self.nodes[self.root]['qubits'] = list(range(max(list(ag.nodes)) + 1))
        self.qubit_to_node = [self.root] * (max(list(ag.nodes)) + 1)
        self.cost_func = cost_func
        # attrs
        self.swap_nodes = None
        self.ag = ag
        self.exchange_log = []

    def clear_attrs(self):
        self.exchange_log = []
        self.swap_nodes = None

    @property
    def depth(self):
        return nx.dag_longest_path_length(self, weight='depth')

    @property
    def node_scores(self):
        node_scores = {}
        depth_ori = self.depth
        for edge in self.edges:
            if not 'depth' in self.edges[edge]: raise ()
            d_ori = self.edges[edge]['depth']
            self.edges[edge]['depth'] = 0
            depth_new = self.depth
            self.edges[edge]['depth'] = d_ori
            node_scores[edge[1]] = depth_ori - depth_new
        return node_scores

    @property
    def cost(self):
        if self.cost_func == 'depth':
            return self.cost_depth
        if self.cost_func == 'depth_tie_break':
            return self.cost_depth_tie_break

    @property
    def cost_depth(self):
        return self.depth

    @property
    def cost_depth_tie_break(self):
        return self.cost_depth + 1 / np.average(self.depths)

    @property
    def depths(self):
        dg_combine = self.combine_2_q_gates()
        depths = []
        for node in dg_combine.nodes:
            if node == dg_combine.root: continue
            if dg_combine.get_node_num_q(node) > 1:
                depths.append(dg_combine.get_node_depth(node))
        return depths

    def get_score(self):
        decay_factor = 0.1
        dg_combine = self.combine_2_q_gates()
        depths = []
        num_qs = []
        for node in dg_combine.nodes:
            if node == dg_combine.root: continue
            if dg_combine.get_node_depth(node) > 3:
                num_qs.append(dg_combine.get_node_num_q(node))
                depths.append(dg_combine.get_node_depth(node))
        depths = np.array(depths)
        num_qs = np.array(num_qs)
        score = np.sum(depths * np.exp(-1 * decay_factor * num_qs))
        return score

    def add_to_exchange_log(self, exchange_nodes):
        self.exchange_log.append(exchange_nodes)

    def from_qasm(self, file, path=None):
        super().from_qasm(file, path=path, absorb=False)
        # extract SWAP gates
        swap_nodes = []
        for node in self.nodes:
            if node == self.root: continue
            name = self.get_node_gates(node)[0][0]
            if name == 'swap': swap_nodes.append(node)
        self.swap_nodes = tuple(swap_nodes)
        # add depth information to each edge
        self.add_depth_to_all_edges()

    def add_depth_to_all_edges(self):
        for edge in self.edges: self.add_depth_to_edge(edge)

    def add_depth_to_edge(self, edge):
        node = edge[1]
        gates = self.get_node_gates(node)
        if len(gates) != 1: raise ()
        self.edges[edge]['depth'] = gate_depth[gates[0][0]]

    def check_node_connectivity(self, node):
        qubits = self.get_node_qubits(node)
        if len(qubits) == 1: return True
        return qubits in self.ag.edges

    def exchangeable(self, node1, node2):
        '''Unimplemented!'''
        raise ()
        pass

    def random_mutation(self, mutate_time, max_try=None):
        '''
        Randomly choose mutate_time node pairs to do exchanging
        Return:
            The number of exchanges having been done.
        '''
        if max_try == None: max_try = mutate_time * 2
        count = 0
        for _ in range(max_try):
            if count >= mutate_time: break
            swap_node = np.random.choice(self.swap_nodes)
            candidate_nodes = list(self.predecessors(swap_node))
            candidate_nodes.extend(list(self.successors(swap_node)))
            # try to pick up the second node to be exchanged
            for _ in range(5):
                non_swap_node = np.random.choice(candidate_nodes)
                if self.exchange(swap_node, non_swap_node):
                    count += 1
                    break
        return count

    def random_mutation2(self, max_try=None):
        '''
        Randomly choose mutate_time node pairs to do exchanging until depth
        is changed.
        Return:
            The number of exchanges having been done.
        '''
        depth_ori = self.depth
        if max_try == None: max_try = 50
        count = 0
        for _ in range(max_try):
            if self.depth != depth_ori: break
            swap_node = np.random.choice(self.swap_nodes)
            candidate_nodes = list(self.predecessors(swap_node))
            candidate_nodes.extend(list(self.successors(swap_node)))
            # try to pick up the second node to be exchanged
            for _ in range(5):
                non_swap_node = np.random.choice(candidate_nodes)
                if self.exchange(swap_node, non_swap_node):
                    count += 1
                    break
        return count

    def random_mutation3(self, max_try):
        '''
        Randomly choose mutate_time node pairs to do exchanging and accept this
        exchange only if cost is decreased.
        Try max_try times
        '''
        cost_current = self.cost
        count = 0
        while count < max_try:
            swap_node = np.random.choice(self.swap_nodes)
            candidate_nodes = list(self.predecessors(swap_node))
            candidate_nodes.extend(list(self.successors(swap_node)))
            # try to pick up the second node to be exchanged
            for _ in range(5):
                non_swap_node = np.random.choice(candidate_nodes)
                if self.exchange(swap_node, non_swap_node):
                    count += 1
                    cost_new = self.cost
                    if cost_new < cost_current:
                        # accept
                        cost_current = cost_new
                    else:
                        # recover
                        self.exchange(swap_node, non_swap_node)
                    break

    def exchange(self, node1, node2):
        '''Exchange the positions of node1 and node2'''
        if node1 == self.root or node2 == self.root: return False
        gate1, gate2 = self.get_node_gates(node1)[0], self.get_node_gates(node2)[0]
        # check commutation
        if node1 == self.root or node2 == self.root: return False
        if gate1[0] == 'swap':
            swap_node, non_swap_node = node1, node2
        else:
            if gate2[0] == 'swap':
                swap_node, non_swap_node = node2, node1
            else:
                return False
                #raise(Exception('Two exchanged nodes must contain at least one SWAP!'))
        if not self.check_direct_dependency(node1, node2): return False
        edge1, edge2 = (node1, node2), (node2, node1)
        edge = None
        if edge1 in self.edges:
            edge = edge1
        if edge2 in self.edges:
            edge = edge2
        if edge == None: raise ()
        # exchange nodes
        swap_qubits = self.get_node_qubits(swap_node)
        ## get shared qubits
        shared_qubits_non_swap = self.get_edge_qubits(edge)
        shared_qubits_swap = swap_qubits_(shared_qubits_non_swap, swap_qubits)
        ## check qubits connectivity after exchanging
        qubits = self.get_node_qubits(non_swap_node)
        qubits_swap = swap_qubits_(qubits, swap_qubits)
        if len(qubits_swap) == 2:
            if not qubits_swap in self.ag.edges: return False
        ## get predecessors and successors
        pre_nodes, succ_nodes = [], []
        for node_pre in list(self.predecessors(edge[0])):
            if edge[0] == swap_node:
                shared_qubits = shared_qubits_swap
            else:
                shared_qubits = shared_qubits_non_swap
            qubits_new = []
            ## delete shared qubits in edges
            for q_pre in self.get_edge_qubits((node_pre, edge[0])):
                if not q_pre in shared_qubits:
                    qubits_new.append(q_pre)
            if len(qubits_new) == 0:
                self.remove_edge(node_pre, edge[0])
                pre_nodes.append(node_pre)
            else:
                if len(qubits_new) < len(self.get_edge_qubits((node_pre, edge[0]))):
                    self.set_edge_qubits((node_pre, edge[0]), qubits_new)
                    pre_nodes.append(node_pre)
        for node_succ in list(self.successors(edge[1])):
            if edge[1] == swap_node:
                shared_qubits = shared_qubits_swap
            else:
                shared_qubits = shared_qubits_non_swap
            qubits_new = []
            ## delete shared qubits in edges
            for q_succ in self.get_edge_qubits((edge[1], node_succ)):
                if not q_succ in shared_qubits:
                    qubits_new.append(q_succ)
            if len(qubits_new) == 0:
                self.remove_edge(edge[1], node_succ)
                succ_nodes.append(node_succ)
            else:
                if len(qubits_new) < len(self.get_edge_qubits((edge[1], node_succ))):
                    self.set_edge_qubits((edge[1], node_succ), qubits_new)
                    succ_nodes.append(node_succ)
        ## swap based exchange
        self.remove_edge(edge[0], edge[1])
        ### update qubits in non-swap node
        self.nodes[non_swap_node]['qubits'] = qubits_swap
        gate = self.get_node_gates(non_swap_node)[0]
        gate_new = gate[0], tuple(swap_qubits_(gate[1], swap_qubits)), gate[2]
        self.nodes[non_swap_node]['gates'] = [gate_new]
        ### add back edge
        self.add_line(edge[1], edge[0])
        self.add_depth_to_edge((edge[1], edge[0]))
        ### add new edges
        for node_pre in pre_nodes:
            self.add_line(node_pre, edge[1])
            self.add_depth_to_edge((node_pre, edge[1]))
        for node_succ in succ_nodes:
            self.add_line(edge[0], node_succ)
            self.add_depth_to_edge((edge[0], node_succ))
        self.exchange_log.append((node1, node2))
        return True

    def cx_to_swap(self):
        '''Try to combine all 3 consecutive CNOTs to 1 SWAP'''
        self.clear_attrs()
        for node in list(self.nodes):
            if node == self.root: continue
            if not node in self.nodes: continue
            swap_nodes = []
            qubits = self.get_node_qubits(node)
            if len(qubits) != 2: continue
            q0, q1 = qubits
            for _ in range(3):
                gates = self.get_node_gates(node)
                if len(gates) != 1: raise ()
                if gates[0][0] != 'cx': break
                q00, q11 = self.get_node_qubits(node)
                if q00 != q0 or q11 != q1:
                    if q00 != q1 or q11 != q0: break
                swap_nodes.append(node)
                if self.out_degree[node] != 1: break
                node = list(self.successors(node))[0]
            if len(swap_nodes) == 3:
                node = self.cascade_node(swap_nodes[0], swap_nodes[1])
                node = self.cascade_node(node, swap_nodes[2])
                self.nodes[node]['gates'] = [('swap', (q0, q1), [])]
                self.nodes[node]['qubits'] = [q0, q1]
                self.nodes[node]['num_gate_1q'], self.nodes[node]['num_gate_2q'] = 0, 1

    def swap_to_cx(self):
        self.clear_attrs()
        for node in self.nodes:
            if node == self.root: continue
            qubits = self.get_node_qubits(node)
            if len(qubits) < 2: continue
            gates = self.get_node_gates(node)
            gates_new = []
            for gate in gates:
                if gate[0] == 'swap' or gate[0] == 'SWAP':
                    q0, q1 = gate[1]
                    gates_new.append(('cx', (q0, q1), []))
                    gates_new.append(('cx', (q1, q0), []))
                    gates_new.append(('cx', (q0, q1), []))
                    self.nodes[node]['num_gate_2q'] += 2
                else:
                    gates_new.append(gate)
            self.nodes[node]['gates'] = gates_new

    def get_node_cx_list(self, node):
        '''If there existing SWAP, we decompose it into 3 CNOTs'''
        cx_list = []
        names = ('cx', 'swap')
        for name, qubits, _ in self.get_node_gates(node):
            if not name in names: raise ()
            if name == 'cx': cx_list.append(tuple(qubits))
            if name == 'swap':
                cx_list.extend([(qubits[0], qubits[1]),
                                (qubits[1], qubits[0]),
                                (qubits[0], qubits[1])])
        return cx_list

    def qcis_circuit(self, add_barrier=False, decompose_swap=False):
        """"
        convert dg to qcis circuit

        Args:
            add_barrier: flag to indicate whether to add barrier.
            decompose_swap: flag to indicate whether to decompose swap operations.
        """
        from copy import deepcopy
        dg = deepcopy(self)
        dg.remove_node(dg.root)
        return super(DGSwap, dg).qcis_circuit(add_barrier=add_barrier,
                                              decompose_swap=decompose_swap)
