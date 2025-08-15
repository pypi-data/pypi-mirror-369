import networkx as nx
from graphviz import Source, Digraph
from .Wrapper import *
from .routine_tree import profile
from .gprof2dot import *
from .QCircuitFeatures import *


def draw_circuit_profile(circuit: Union[pq.QCircuit, pq.QProg], gate_times: dict, is_show: bool = False, out_file: str = None):
    """
    Draw a profile of the quantum circuit's performance.

    @param circuit:
        The quantum circuit object to be drawn, containing the structure and information of the circuit.

    @param gate_times:
        A dictionary where the keys are the names of the quantum gates and the values are the execution times
        of each gate (units can be seconds or milliseconds).

    @param is_show:
        A boolean flag indicating whether to display the graph after drawing. Defaults to False.

    @param out_file:
        The path and filename to save the output. If provided, the graph will be saved to this file.
        If None, the graph will not be saved.

    @return
        None,
        This function does not return a value but will draw the performance profile of the quantum circuit
        and may save it to a file or display it based on the provided parameters.
    """

    if isinstance(circuit, pq.QProg):
        circuit = circuit.to_circuit()
    qprof_out = profile(circuit, gate_times, wrapper=QPandaWrapper)
    print(qprof_out)
    dot_str = gprof2dot(qprof_out)
    print(dot_str)
    source = Source(dot_str, format='png')

    if is_show:
        source.view()
    if out_file:
        out_file = '.'.join(out_file.split('.')[:-1])
        source.render(out_file, format='png', cleanup=True)


def _find_layers(G):
    layers = []
    G_copy = G.copy()

    while G_copy.number_of_nodes() > 0:
        current_layer = [node for node in G_copy.nodes() if G_copy.in_degree(node) == 0]

        if not current_layer:
            break

        layers.append(current_layer)

        G_copy.remove_nodes_from(current_layer)

    return layers


def draw_circuit_DAG(circuit: pq.QCircuit, is_show: bool = False, save_fn=None):
    """
    Draw the Directed Acyclic Graph (DAG) representation of the quantum circuit.

    @param circuit:
        The quantum circuit object to be drawn, which contains the structure and details of the circuit.

    @param is_show:
        A boolean flag indicating whether to display the DAG graph after drawing. Defaults to False.

    @param save_fn:
        A function or method to save the generated DAG representation. If provided, the graph will be saved
        according to the specified function. If None, the graph will not be saved.

    @return
        None,
        This function does not return a value but will draw the DAG representation of the quantum circuit
        and may display it or save it based on the provided parameters.
    """
    dag = pq.DAGQCircuit()
    dag.from_circuit(circuit)
    nodes = dag.nodes()
    edges = dag.edges()
    gates = dag.gates()
    labels = dict()
    for node in nodes:
        labels[node] = f'{gates[node].name()}{gates[node].qubits()}'

    dot = Digraph(name="MyPicture", comment="the test", format="png")

    G = nx.DiGraph()
    G.add_edges_from(edges)
    layers = _find_layers(G)

    for i, layer in enumerate(layers):
        print(f"Layer {i + 1}: {[labels[idx] for idx in layer]}")
        with dot.subgraph(name=f'cluster_{i}') as c:
            c.attr(rank='same')
            c.attr(style='dotted', color='lightgrey')
            c.node(f'Layer {i}', f'Layer {i}', shape='plaintext')
            for node in layer:
                # x = gates[node].qubits()[-1]
                qubits = gates[node].qubits()
                x = sum(qubits) / len(qubits)

                y = len(layers) - i
                width = max(qubits) - min(qubits)
                c.node(str(node), labels[node], shape='rect', color='#6fa4fe')

    # for node in nodes:
    #     dot.node(str(node), labels[node], shape='rect', color='#6fa4fe')

    for start, end in edges:
        dot.edge(str(start), str(end), color='#6fa4fe')

    if is_show:
        dot.view(filename="mypicture", directory="./")
    if save_fn:
        save_fn = '.'.join(save_fn.split('.')[:-1])
        dot.render(save_fn, format='png', cleanup=True)

    # print([labels[i] for i in dag.longest_path()])


def draw_circuit_features(circuit: Union[pq.QCircuit, pq.QProg], is_show: bool = False, save_fn: str = None,
                          title: str = ''):
    """
    @brief Draws the features of a quantum circuit and visualizes them as a radar chart.

    This function takes a quantum circuit or program as input, computes various features
    such as connectivity, liveness, parallelism, entanglement, and depth, and then plots
    these features in a radar chart.

    @param circuit The quantum circuit or program to analyze. This can be either
                   an instance of `pq.QCircuit` or `pq.QProg`.
    @param is_show A boolean flag indicating whether to display the plot.
                   Defaults to False.
    @param save_fn An optional string for the filename to save the plot. If None,
                   the plot will not be saved.
    @param title An optional title for the plot. Defaults to an empty string.

    @return None This function does not return any value. It directly generates
                  and displays the radar chart based on the computed features.

    @note The function computes the following features:
          - Connectivity
          - Liveness
          - Parallelism
          - Entanglement
          - Critical Depth
    """
    labels = []
    feature_vecs = []
    if isinstance(circuit, pq.QCircuit):
        circ = circuit
    elif isinstance(circuit, pq.QProg):
        circ = circuit.to_circuit()
    use_qubit = len(circ.qubits())

    # Draw radar map

    labels.append(f'{use_qubit} qubits')
    con = compute_connectivity(circ)
    liv = compute_liveness(circ)
    par = compute_parallelism(circ)
    # mea = compute_measurement(circ)
    ent = compute_entanglement(circ)
    dep = compute_depth(circ)
    feature_vecs.append([con, liv, par, ent, dep])
    print(feature_vecs)
    spoke_labels = ['Program Communication', 'Liveness', 'Parallelism', 'Entanglement', 'Critical Depth']
    plot_benchmark([title, labels, feature_vecs], spoke_labels=spoke_labels, legend_loc=(0.1, 0.25),
                   savefn=save_fn, show=is_show)
