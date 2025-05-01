import random

import networkx as nx
from reason.tools.graph.iso_fun import isomorphic_functions, isomorphic_dicts


class IsomorphismLab:
    def __init__(self, graph, nodes_color_map=None, edges_color_map=None):
        self.graph = graph
        self.is_directed = isinstance(self.graph, nx.DiGraph)

        if nodes_color_map is not None:
            self.nodes_color_map = dict(nodes_color_map)
        else:
            self.nodes_color_map = None

        if edges_color_map is not None:
            self.edges_color_map = dict(edges_color_map)
        else:
            self.edges_color_map = None

        self.names = {}

        if not self.is_directed:
            self.symmetrize_edges_color_map()
            self.init_naming = self.init_naming_not_directed
            self.get_signature_edges = self.get_signature_edges_for_not_directed
        else:
            self.init_naming = self.init_naming_directed
            self.get_signature_edges = self.get_signature_edges_for_directed

    def symmetrize_edges_color_map(self):
        if self.edges_color_map is not None:
            keys = list(self.edges_color_map.keys())
            for a, b in keys:
                self.edges_color_map[b, a] = self.edges_color_map[a, b]

    def shorten_names(self):
        names = [self.names[n] for n in self.graph.nodes()]
        names.sort()
        names_map = {}
        for n in names:
            if n not in names_map:
                names_map[n] = len(names_map)
        for node in self.graph.nodes():
            self.names[node] = names_map[self.names[node]]

    def init_naming_not_directed(self):
        for node in self.graph.nodes():
            if self.nodes_color_map is not None and node in self.nodes_color_map:
                self.names[node] = self.graph.degree[node], (self.nodes_color_map[node],)
            else:
                self.names[node] = (self.graph.degree[node], tuple())

    def init_naming_directed(self):
        for node in self.graph.nodes():
            if self.nodes_color_map is not None and node in self.nodes_color_map:
                self.names[node] = self.graph.out_degree[node], (self.nodes_color_map[node],)
            else:
                self.names[node] = (self.graph.out_degree[node], tuple())

    def renaming_step(self):
        prev_names = dict(self.names)

        for node in self.graph.nodes():
            names = []
            for neighbor in self.graph.neighbors(node):
                name = prev_names[neighbor]

                if self.edges_color_map is not None and (node, neighbor) in self.edges_color_map:
                    name = name, (self.edges_color_map[node, neighbor],)
                else:
                    name = name, tuple()

                names.append(name)

            names.sort()
            if self.nodes_color_map is not None and node in self.nodes_color_map:
                self.names[node] = tuple(names), (self.nodes_color_map[node],)
            else:
                self.names[node] = tuple(names), tuple()

        return prev_names

    def get_signature_edges_for_not_directed(self):
        edges = []
        for n1, n2 in self.graph.edges():
            name1 = self.names[n1]
            name2 = self.names[n2]
            if self.edges_color_map is not None and ((n1, n2) in self.edges_color_map):
                if name1 > name2:
                    edges.append((name2, name1, (self.edges_color_map[n2, n1],)))
                else:
                    edges.append((name1, name2, (self.edges_color_map[n1, n2],)))
            else:
                if name1 > name2:
                    edges.append((name2, name1, tuple()))
                else:
                    edges.append((name1, name2, tuple()))

        return edges

    def get_signature_edges_for_directed(self):
        edges = []
        for n1, n2 in self.graph.edges():
            name1 = self.names[n1]
            name2 = self.names[n2]
            if self.edges_color_map is not None and ((n1, n2) in self.edges_color_map):
                edges.append((name1, name2, (self.edges_color_map[n1, n2],)))
            else:
                edges.append((name1, name2, tuple()))

        return edges

    def signature(self):
        prev_names = {}
        self.init_naming()
        k = 0
        while not isomorphic_dicts(self.names, prev_names):
            prev_names = self.renaming_step()
            self.shorten_names()
            k += 1

        nodes = []
        for n in self.graph.nodes():
            if self.nodes_color_map is not None and n in self.nodes_color_map:
                nodes.append((self.names[n], (self.nodes_color_map[n],)))
            else:
                nodes.append((self.names[n], tuple()))
        nodes.sort()

        edges = self.get_signature_edges()

        edges.sort()

        return tuple(nodes + edges)

    def isomorphic_copy(self):
        nodes = list(self.graph.nodes())
        random.shuffle(nodes)

        nodes_map = dict(zip(self.graph.nodes(), nodes))

        if not self.is_directed:
            res_graph = nx.Graph()
        else:
            res_graph = nx.DiGraph()

        for n in self.graph.nodes():
            res_graph.add_node(nodes_map[n])

        for n1, n2 in self.graph.edges():
            res_graph.add_edge(nodes_map[n1], nodes_map[n2])

        nodes_color_map = None
        if self.nodes_color_map is not None:
            nodes_color_map = {nodes_map[n]: self.nodes_color_map[n] for n in self.nodes_color_map}

        edges_color_map = None
        if self.edges_color_map is not None:
            edges_color_map = {
                (nodes_map[a], nodes_map[b]): self.edges_color_map[a, b] for (a, b) in self.edges_color_map
            }

        return res_graph, nodes_color_map, edges_color_map
