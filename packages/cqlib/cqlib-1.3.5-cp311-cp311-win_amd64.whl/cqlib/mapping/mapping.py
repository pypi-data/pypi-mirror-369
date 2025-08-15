#  This code is part of cqlib.
#  #
#  (C) Copyright qc.zdxlz.com 2024.
#  #
#  This code is licensed under the Apache License, Version 2.0. You may
#  obtain a copy of this license in the LICENSE.txt file in the root directory
#  of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#  #
#  Any modifications or derivative works of this code must retain this
#  copyright notice, and modified files need to carry a notice indicating
#  that they have been altered from the originals.
#
import re

from .cir_dg import DG
import networkx as nx
import numpy as np
from .monte_carlo_tree import MCTree
from cqlib import BasePlatform, Circuit

method_init_mapping = 'Topgraph'


def layout_dict_to_list(layout_dict):
    num_q_log = max(list(layout_dict.keys())) + 1
    layout_list = [-1] * num_q_log
    for key in layout_dict.keys():
        layout_list[key] = layout_dict[key]
    return layout_list


def layout_list_to_dict(layout_list):
    layout_dict = {}
    for i, v in enumerate(layout_list):
        layout_dict[i] = v
    return layout_dict


def layout_dict_reverse(layout_dict):
    layout_dict_r = {v: k for k, v in layout_dict.items()}
    return layout_dict_r


from .init_mapping.get_init_map import get_init_map


def get_adjacent_list(platform: BasePlatform):
    config = platform.download_config()
    couplers_map = config['overview']['coupler_map']
    unused_couplers = config['disabledCouplers'].split(',')
    adjacent_list = [(int(qubit_pairs[0].lstrip('Q')), int(qubit_pairs[1].lstrip('Q'))) for c, qubit_pairs in
                     couplers_map.items() if c not in unused_couplers]
    return adjacent_list


def create_ag_from_chip_structure(platform: BasePlatform):
    adjacent_list = get_adjacent_list(platform)
    ag = nx.Graph()
    ag.add_edges_from(adjacent_list)
    if not nx.is_connected(ag):
        # if ag is not fully connected, we use subgraph with the largest connected component.
        sub_ag_node_list = max(nx.connected_components(ag), key=len)
        ag = ag.subgraph(sub_ag_node_list)

    ag.shortest_length = dict(nx.shortest_path_length(ag, source=None,
                                                      target=None,
                                                      weight=None,
                                                      method='dijkstra'))
    ag.shortest_length_weight = ag.shortest_length
    ag.shortest_path = nx.shortest_path(ag, source=None, target=None,
                                        weight=None, method='dijkstra')
    return ag


def generate_qubit_mapping(qcis_str):
    mapping = {}
    line_pattern = re.compile(r'^([A-Z][A-Z0-9]*)\s+((?:Q[0-9]+\s*)+)(.*)')
    qcis = []
    for line in qcis_str.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('PLS ') or line.startswith('PULSE '):
            raise ValueError("PULSE/PLS not supported")
        match = line_pattern.match(line)
        if not match:
            raise ValueError(f'Invalid line format: {line}')
        gate, qubits_str, params_str = match.groups()
        qubits = []
        for q in qubits_str.split():
            i = int(q[1:])
            mapping.setdefault(i, len(mapping))
            qubits.append(f'Q{mapping[i]}')
        qcis.append(' '.join([gate, ' '.join(qubits), params_str]))
    return mapping, '\n'.join(qcis)


def transpile_qcis(qcis_str, platform: BasePlatform, initial_layout=None, objective='size',
                   seed=None):
    """
    The script transpiles qasm string by searching for a mapping from virtual to physical qubit
    and a swap strategy such that the circuit described by qasm can be fitted into a hardware
    described by the coupling_map, in the meanwhile reduces circuit depth.

    Parameters
    ----------
    qcis_str : string
        qcis string
    platform : instance of BasePlatform to retrieve chip structure.
    initial_layout : dict, optional
        Initial position of virtual qubits on physical qubits.
        If given, this is the initial state in search of virtual to physical qubit mapping
        e.g.:
            {0:4, 1:1, 2:5, 3:2, 4:0, 5:3}
        The default is None.
    objective:
        size: min. # of added swaps
        depth: min. depth
        no_swap: try best to find an initial mapping requiring no swaps; raise
        an error if fail
    seed : integer, optional
        Set random seed for the stochastic part of the tranpiler
        The default is None.
    use_post_opt: we provide a genetic alg. which utilizes exchange rules for
        swaps to futher min. depth.

    Returns
    -------
    res: list
        circuit : Circuit
            New circuit object.
        layout : dict
            mapping from virtual to physical qubit
            e.g.:
                {0:1, 1:2, 2:3, 3:4, 4:0}
        swap_mapping : dict
            mapping from initial physical qubit to final physical qubit after a series of swaps
            e.g.:
                {0:1, 1:2, 2:3, 3:4, 4:0}
        mapping_virtual_to_final:
            mapping from virtual to final physical qubit

    raised:
        TranspileError:
           if graph specified by coupling map is disconnected

    Args:
        platform:

    """
    ag = create_ag_from_chip_structure(platform)
    # parameters for MCT search process
    selec_times = 50  # recommend:50 for realistic circuits
    select_mode = ['KS', 15]
    use_prune = 1
    use_hash = 1
    # init objective
    score_layer = 5
    # generate dependency graph
    dg = DG()
    qubit_mapping, qcis_str = generate_qubit_mapping(qcis_str)

    m_instructs = dg.from_qcis_str(qcis_str)
    num_q_vir = dg.num_q
    # initial mapping
    if initial_layout is None:
        init_map = get_init_map(dg, ag, method_init_mapping)
        initial_layout = layout_list_to_dict(init_map)
    else:
        initial_layout = {qubit_mapping[k]: v for k, v in initial_layout.items()}
    # init search tree
    search_tree = MCTree(ag, dg,
                         objective=objective,
                         select_mode=select_mode,
                         score_layer=score_layer,
                         use_prune=use_prune,
                         use_hash=use_hash,
                         init_mapping=initial_layout)
    # MCT search process
    while search_tree.nodes[search_tree.root_node]['num_remain_gates'] > 0:
        # for _ in range(selec_times):
        while search_tree.selec_count < selec_times:
            # selection
            exp_node, _ = search_tree.selection()
            # EXP
            search_tree.expansion(exp_node)
        # decision
        search_tree.decision()
    dg_qct = search_tree.to_dg()
    dg_qct.num_q = max(list(ag.nodes)) + 1
    qcis_circuit = dg_qct.qcis_circuit(add_barrier=False)
    # get swap mapping
    swaps = search_tree.get_swaps()
    swap_mapping = list(range(max(list(ag.nodes)) + 1))
    for swap in swaps:
        t0, t1 = swap_mapping[swap[0]], swap_mapping[swap[1]]
        swap_mapping[swap[0]], swap_mapping[swap[1]] = t1, t0
    swap_mapping = layout_dict_reverse(layout_list_to_dict(swap_mapping))
    mapping_virtual_to_final = {i: swap_mapping[initial_layout[i]] for i in range(len(ag))}
    # add back measurements which assume all measurements are added at the end of the order
    new_q_index = [mapping_virtual_to_final[q] for q in m_instructs]
    for q in new_q_index:
        qcis_circuit.measure(q)
    # delete redundant qubits
    for q in list(initial_layout.keys()):
        if q >= num_q_vir:
            initial_layout.pop(q)
            mapping_virtual_to_final.pop(q)
    r_qubit_mapping = {v: k for k, v in qubit_mapping.items()}
    initial_layout = {r_qubit_mapping[k]: v for k, v in initial_layout.items()}
    mapping_virtual_to_final = {r_qubit_mapping[k]: v for k, v in mapping_virtual_to_final.items()}
    c = Circuit.load(qcis_circuit.as_str())
    return c, initial_layout, swap_mapping, mapping_virtual_to_final
