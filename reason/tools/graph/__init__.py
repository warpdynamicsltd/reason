import random
import networkx as nx
from reason.tools.graph.iso_fun import isomorphic_functions, isomorphic_dicts


class IsomorphismLab:
    def __init__(self, graph, nodes_color_map=None, edges_color_map=None):
        self.graph = graph

        if nodes_color_map is not None:
            self.nodes_color_map = dict(nodes_color_map)
        else:
            self.nodes_color_map = None

        if edges_color_map is not None:
            self.edges_color_map = dict(edges_color_map)
        else:
            self.edges_color_map = None

        self.names = {}

        # self.normalise()
        self.symmetrize_edges_color_map()

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

    def init_naming(self):
        # if self.nodes_color_map is None:
        #     for node in self.graph.nodes():
        #         self.names[node] = tuple(), self.graph.degree[node]
        # else:
        #     for node in self.graph.nodes():
        #         if node in self.nodes_color_map:
        #             self.names[node] = (self.nodes_color_map[node],), self.graph.degree[node]
        #         else:
        #             self.names[node] = (tuple(), self.graph.degree[node])

        for node in self.graph.nodes():
            if self.nodes_color_map is not None and node in self.nodes_color_map:
                self.names[node] = (self.nodes_color_map[node],), self.graph.degree[node]
            else:
                self.names[node] = (tuple(), self.graph.degree[node])

    def renaming_step(self):
        prev_names = dict(self.names)

        for node in self.graph.nodes():
            names = []
            for neighbor in self.graph.neighbors(node):
                name = prev_names[neighbor]

                if self.edges_color_map is not None and (node, neighbor) in self.edges_color_map:
                    name = (self.edges_color_map[node, neighbor],), name
                else:
                    name = tuple(), name

                names.append(name)

            names.sort()
            if self.nodes_color_map is None:
                self.names[node] = tuple(), tuple(names)
            else:
                if node in self.nodes_color_map:
                    self.names[node] = (self.nodes_color_map[node],), tuple(names)
                else:
                    self.names[node] = tuple(), tuple(names)

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
            if self.nodes_color_map is not None and n in self.nodes_color_map:
                nodes.append((self.names[n], (self.nodes_color_map[n],)))
            else:
                nodes.append((self.names[n], tuple()))
        nodes.sort()

        edges = []
        for n1, n2 in self.graph.edges():
            name1 = self.names[n1]
            name2 = self.names[n2]
            if self.edges_color_map is not None and ((n1, n2) in self.edges_color_map):
                if name1 > name2:
                    edges.append((name2, name1, (self.edges_color_map[n1, n2],)))
                else:
                    edges.append((name1, name2, (self.edges_color_map[n1, n2],)))
            else:
                if name1 > name2:
                    edges.append((name2, name1, tuple()))
                else:
                    edges.append((name1, name2, tuple()))
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

        # if self.nodes_color_map is not None:
        #     return res_graph, {nodes_map[n]: self.nodes_color_map[n] for n in self.graph.nodes()}
        # else:
        #     return res_graph, None
