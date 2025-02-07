import random
import networkx as nx
from reason.tools.graph.iso_fun import isomorphic_functions, isomorphic_dicts


class IsomorphismLab:
    def __init__(self, graph, color_map=None):
        self.graph = graph
        self.color_map = color_map
        self.names = {}

    def shorten_names(self):
        names = [self.names[n] for n in self.graph.nodes()]
        names.sort()
        names_map = {}
        for n in names:
            if n not in names_map:
                names_map[n] = len(names_map)

        for node in self.graph.nodes():
            self.names[node] = names_map[self.names[node]]

    def init_naming(self):
        if self.color_map is None:
            for node in self.graph.nodes():
                self.names[node] = self.graph.degree[node]
        else:
            for node in self.graph.nodes():
                self.names[node] = self.color_map[node], self.graph.degree[node]

    def renaming_step(self):
        prev_names = dict(self.names)

        for node in self.graph.nodes():
            names = []
            for neighbor in self.graph.neighbors(node):
                name = prev_names[neighbor]
                names.append(name)

            names.sort()
            if self.color_map is None:
                self.names[node] = tuple(names)
            else:
                self.names[node] = self.color_map[node], tuple(names)

        return prev_names

    def signature(self):
        prev_names = {}
        self.init_naming()
        k = 0
        while not isomorphic_dicts(self.names, prev_names):
            prev_names = self.renaming_step()
            self.shorten_names()
            k += 1

        # print(k)

        nodes = []
        for n in self.graph.nodes():
            nodes.append(self.names[n])
        nodes.sort()

        edges = []
        for n1, n2 in self.graph.edges():
            name1 = self.names[n1]
            name2 = self.names[n2]
            if name1 > name2:
                edges.append((name2, name1))
            else:
                edges.append((name1, name2))
        edges.sort()

        return tuple(nodes + edges)

    def isomorphic_copy(self):
        nodes = list(self.graph.nodes())
        random.shuffle(nodes)

        nodes_map = dict(zip(self.graph.nodes(), nodes))
        res_graph = nx.Graph()

        for n in self.graph.nodes():
            res_graph.add_node(nodes_map[n])

        for n1, n2 in self.graph.edges():
            res_graph.add_edge(nodes_map[n1], nodes[n2])

        if self.color_map is not None:
            return res_graph, {nodes_map[n]: self.color_map[n] for n in self.graph.nodes()}
        else:
            return res_graph, None
