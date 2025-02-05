import random
import networkx as nx
from reason.tools.graph.iso_fun import isomorphic_functions


class IsomorphismLab:
    @staticmethod
    def shorten_names(graph):
        names = [graph.nodes[n]["name"] for n in graph.nodes()]
        names.sort()
        names_map = {}
        for n in names:
            if n not in names_map:
                names_map[n] = len(names_map)

        for node in graph.nodes():
            graph.nodes[node]["name"] = names_map[graph.nodes[node]["name"]]

    @staticmethod
    def renaming_step(graph):
        for node in graph.nodes():
            graph.nodes[node]["prev_name"] = graph.nodes[node]["name"]

        for node in graph.nodes():
            names = []
            for neighbor in graph.neighbors(node):
                names.append(graph.nodes[neighbor]["prev_name"])

            names.sort()
            graph.nodes[node]["name"] = tuple(names)

    @staticmethod
    def init_naming(graph):
        for node in graph.nodes():
            graph.nodes[node]["name"] = graph.degree[node]
            graph.nodes[node]["prev_name"] = None

    @staticmethod
    def signature(graph):
        IsomorphismLab.init_naming(graph)
        k = 0
        while not isomorphic_functions(
            lambda n: graph.nodes[n]["name"], lambda n: graph.nodes[n]["prev_name"], graph.nodes()
        ):
            IsomorphismLab.renaming_step(graph)
            IsomorphismLab.shorten_names(graph)
            k += 1

        # print(k)
        edges = list(graph.edges())
        edges.sort()
        return tuple(edges)

    @staticmethod
    def isomorphic_copy(graph):
        nodes = list(graph.nodes())
        random.shuffle(nodes)

        nodes_map = dict(zip(nodes, graph.nodes()))
        res_graph = nx.Graph()
        for n1, n2 in graph.edges():
            res_graph.add_edge(nodes_map[n1], nodes[n2])

        return graph
