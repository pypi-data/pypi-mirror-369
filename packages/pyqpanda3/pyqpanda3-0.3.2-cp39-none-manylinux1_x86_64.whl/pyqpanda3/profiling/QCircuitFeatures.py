import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from typing import Union

import pyqpanda3.core as pq


def compute_connectivity(circuit: pq.QCircuit) -> float:
    N = max(circuit.qubits()) + 1
    dag = pq.DAGQCircuit()
    dag.from_circuit(circuit)
    dag.build()
    G = nx.Graph()
    for gate in dag.two_qubit_gates():
        if gate.is_controlled():
            q1 = gate.m_target_qubits[0]
            q2 = gate.m_control_qubits[0]
        else:
            q1 = gate.m_target_qubits[0]
            q2 = gate.m_target_qubits[1]
        G.add_edge(q1, q2)

    degree_sum = sum([G.degree(n) for n in G.nodes])

    return degree_sum / (N * (N - 1))


def compute_liveness(circuit: pq.QCircuit) -> float:
    N = max(circuit.qubits()) + 1
    dag = pq.DAGQCircuit()
    dag.from_circuit(circuit)
    dag.build()
    depth = len(dag.layers())
    activity_matrix = np.zeros((N, depth))

    for i, layer in enumerate(dag.layers()):
        for gate_idx in layer:
            gate = dag.get_gate(gate_idx)
            for qubit in gate.m_target_qubits + gate.m_control_qubits:
                activity_matrix[qubit, i] = 1

    return np.sum(activity_matrix) / (N * depth)


def compute_parallelism(circuit: pq.QCircuit) -> float:
    dag = pq.DAGQCircuit()
    dag.from_circuit(circuit)
    dag.build()
    depth = len(dag.layers())
    return max(1 - (depth / len(dag.gates())), 0)


def compute_measurement(circuit: pq.QCircuit) -> float:
    return 0


def compute_entanglement(circuit: pq.QCircuit) -> float:
    dag = pq.DAGQCircuit()
    dag.from_circuit(circuit)
    dag.build()
    return len(dag.two_qubit_gates()) / len(dag.gates())


def compute_depth(circuit: pq.QCircuit) -> float:
    N = len(circuit.qubits())

    dag = pq.DAGQCircuit()
    dag.from_circuit(circuit)
    dag.build()
    n_ed = 0
    two_q_nodes = [node for node in dag.two_qubit_gate_nodes()]
    path = dag.longest_path()
    for node in two_q_nodes:
        if node in path:
            n_ed += 1

    n_e = len(dag.two_qubit_gates())

    if n_ed == 0:
        return 0

    return n_ed / n_e


def radar_factory(num_vars, frame="circle"):
    """
    (https://matplotlib.org/stable/gallery/specialty_plots/radar_chart.html)

    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = "radar"
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location("N")

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels, fontsize=14)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == "circle":
                return Circle((0.5, 0.5), 0.5)
            elif frame == "polygon":
                return RegularPolygon((0.5, 0.5), num_vars, radius=0.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == "circle":
                return super()._gen_axes_spines()
            elif frame == "polygon":
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(
                    axes=self, spine_type="circle", path=Path.unit_regular_polygon(num_vars)
                )
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes)
                return {"polar": spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def plot_benchmark(data, show=True, savefn=None, spoke_labels=None, legend_loc=(0.75, 0.85)):
    """
    Create a radar plot of the given benchmarks.

    Input
    -----
    data : List
        Contains the title, feature data, and labels in the format:
        [title, [labels], [feature vecs: [con, liv, par, mea, ent] ]]
    """
    plt.rcParams["font.family"] = "Times New Roman"

    if spoke_labels is None:
        spoke_labels = ["Connectivity", "Liveness", "Parallelism", "Measurement", "Entanglement"]

    N = len(spoke_labels)
    theta = radar_factory(N, frame="circle")

    fig, ax = plt.subplots(dpi=150, subplot_kw=dict(projection="radar"))
    # fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    title, labels, case_data = data
    # ax.set_rgrids([0.2, 0.4, 0.6, 0.8])
    ax.set_rgrids([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylim(0, 1)
    ax.set_title(title, weight='bold', size=16, position=(0.5, 1.1))
    #             horizontalalignment='center', verticalalignment='center')
    for d, label in zip(case_data, labels):
        ax.plot(theta, d, label=label)
        ax.fill(theta, d, alpha=0.25)
    ax.set_varlabels(spoke_labels)

    ax.legend(loc=legend_loc, labelspacing=0.1, fontsize=11)
    plt.tight_layout()

    if savefn is not None:
        plt.savefig(savefn)

    if show:
        plt.show()

    plt.close()


