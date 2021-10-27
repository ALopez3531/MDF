"""
    Example of ModECI MDF - Testing integrate and fire neurons
"""

from modeci_mdf.mdf import *
import sys


def main():
    mod = Model(id="IAFs")
    mod_graph = Graph(id="iaf_example")
    mod.graphs.append(mod_graph)

    ## Counter node
    input_node = Node(id="input_node")

    t_param = Parameter(id="t", default_initial_value=0, time_derivative="1")
    input_node.parameters.append(t_param)

    p0 = Parameter(id="initial", value=-3)
    input_node.parameters.append(p0)
    p1 = Parameter(id="rate", value=0.2)
    input_node.parameters.append(p1)

    p2 = Parameter(id="level", value="initial + rate*t")
    input_node.parameters.append(p2)

    op1 = OutputPort(id="out_port", value=p2.id)
    input_node.output_ports.append(op1)
    op2 = OutputPort(id="t_out_port", value=t_param.id)
    input_node.output_ports.append(op2)

    mod_graph.nodes.append(input_node)

    ## IAF node...
    iaf_node = Node(id="iaf_node")
    ip1 = InputPort(id="input")
    iaf_node.input_ports.append(ip1)

    erev = Parameter(id="erev", value=-70)
    iaf_node.parameters.append(erev)
    tau = Parameter(id="tau", value=10)
    iaf_node.parameters.append(tau)
    thresh = Parameter(id="thresh", value=-20)
    iaf_node.parameters.append(thresh)
    # v_init = Parameter(id="v_init", value=-30)
    # iaf_node.parameters.append(v_init)

    v = Parameter(
        id="v", default_initial_value="-50", time_derivative="-1 * (v-erev)/tau + input"
    )
    iaf_node.parameters.append(v)

    op1 = OutputPort(id="out_port", value="v")
    iaf_node.output_ports.append(op1)
    mod_graph.nodes.append(iaf_node)

    e1 = Edge(
        id="input_edge",
        parameters={"weight": 1},
        sender=input_node.id,
        sender_port=op1.id,
        receiver=iaf_node.id,
        receiver_port=ip1.id,
    )

    mod_graph.edges.append(e1)

    new_file = mod.to_json_file("%s.json" % mod.id)
    new_file = mod.to_yaml_file("%s.yaml" % mod.id)

    if "-run" in sys.argv:
        verbose = True
        verbose = False
        from modeci_mdf.utils import load_mdf, print_summary

        from modeci_mdf.execution_engine import EvaluableGraph

        eg = EvaluableGraph(mod_graph, verbose)
        dt = 0.1

        duration = 100
        t_ext = 0
        recorded = {}
        times = []
        t = []
        i = []
        s = []
        while t_ext <= duration:
            times.append(t_ext)
            print("======   Evaluating at t = %s  ======" % (t_ext))
            if t == 0:
                eg.evaluate()  # replace with initialize?
            else:
                eg.evaluate(time_increment=dt)

            i.append(eg.enodes["input_node"].evaluable_outputs["out_port"].curr_value)
            t.append(eg.enodes["input_node"].evaluable_outputs["t_out_port"].curr_value)
            s.append(eg.enodes["iaf_node"].evaluable_outputs["out_port"].curr_value)
            t_ext += dt

        if "-nogui" not in sys.argv:
            import matplotlib.pyplot as plt

            plt.plot(times, t, label="time at input node")
            plt.plot(times, i, label="state of input node")
            plt.plot(times, s, label="IaF 0 state")
            plt.legend()
            plt.show()

    if "-graph" in sys.argv:
        mod.to_graph_image(
            engine="dot",
            output_format="png",
            view_on_render=False,
            level=3,
            filename_root="iaf",
            only_warn_on_fail=True,  # Makes sure test of this doesn't fail on Windows on GitHub Actions
        )

    return mod_graph


if __name__ == "__main__":
    main()
