import unittest

import random
import numpy as np
import networkx as nx

from reason.tools.graph.gen import random_graph
from reason.tools.graph import IsomorphismLab

def random_color_map(graph, k=2, p=1):
    return {n: random.choice(range(k)) for i, n in enumerate(graph.nodes()) if random.random() <= p}

def random_edges_color_map(graph, k=2, p=1):
    return {(a, b): random.choice(range(k)) for i, (a, b) in enumerate(graph.edges()) if random.random() <= p}

def add_random_edges(G, num_edges):
    nodes = list(G.nodes())
    added = 0
    while added < num_edges:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            G.add_edge(u, v)
            added += 1

def random_non_iso_connected_graphs(n=20, p=0.2, num_added_edges=5, is_directed=False):
    binary_matrix = (np.random.rand(n, n) < p).astype(int)
    np.fill_diagonal(binary_matrix, 0)

    if not is_directed:
        binary_matrix = np.maximum(binary_matrix, binary_matrix.T)
        G = nx.from_numpy_array(binary_matrix)
        connected_components = nx.connected_components(G)
    else:
        G = nx.from_numpy_array(binary_matrix, create_using=nx.DiGraph())
        connected_components = nx.strongly_connected_components(G)



    # Find the largest one
    largest_cc = max(connected_components, key=len)

    # Create a subgraph of just that component
    resG = G.subgraph(largest_cc).copy()
    largerG = resG.copy()
    add_random_edges(largerG, num_added_edges)

    return resG, largerG


class TestSignature(unittest.TestCase):
    def random_small_graph(self, seed: int, nodes_map=True, edges_map=True, p=1.0, k=2, is_directed=False):
        np.random.seed(seed)
        random.seed(seed)

        G1, G2 = random_non_iso_connected_graphs(is_directed=is_directed)

        if nodes_map:
            nodes_color_map1 = random_color_map(G1, k=k, p=p)
            nodes_color_map2 = random_color_map(G2, k=k, p=p)
            nodes_color_map1_rnd = random_color_map(G1, k=k, p=p)
        else:
            nodes_color_map1 = None
            nodes_color_map2 = None
            nodes_color_map1_rnd = None

        if edges_map:
            edges_color_map1 = random_edges_color_map(G1, k=k, p=p)
            edges_color_map2 = random_edges_color_map(G1, k=k, p=p)
            edges_color_map1_rnd = random_edges_color_map(G1, k=k, p=p)
        else:
            edges_color_map1 = None
            edges_color_map2 = None
            edges_color_map1_rnd = None



        iso1 = IsomorphismLab(G1, nodes_color_map=nodes_color_map1, edges_color_map=edges_color_map1)
        G1_iso, nodes_color_map1_iso, edges_color_map1_iso = iso1.isomorphic_copy()

        iso2 = IsomorphismLab(G2, nodes_color_map=nodes_color_map2, edges_color_map=edges_color_map2)
        G2_iso,nodes_color_map2_iso, edges_color_map2_iso = iso2.isomorphic_copy()



        self.assertEqual(iso1.signature(), IsomorphismLab(G1_iso,
                                                          nodes_color_map=nodes_color_map1_iso,
                                                          edges_color_map=edges_color_map1_iso).signature())

        if nodes_color_map1_rnd is not None or edges_color_map1_rnd is not None:
            self.assertNotEqual(iso1.signature(), IsomorphismLab(G1_iso,
                                                                 nodes_color_map=nodes_color_map1_rnd,
                                                                 edges_color_map=edges_color_map1_rnd).signature())

        self.assertEqual(iso2.signature(), IsomorphismLab(G2_iso,
                                                          nodes_color_map=nodes_color_map2_iso,
                                                          edges_color_map=edges_color_map2_iso).signature())

        self.assertNotEqual(iso1.signature(), IsomorphismLab(G2).signature())

        if nodes_color_map1_rnd is not None or edges_color_map1_rnd is not None:
            self.assertNotEqual(iso2.signature(), IsomorphismLab(G1,
                                                                 nodes_color_map=nodes_color_map1_rnd,
                                                                 edges_color_map=edges_color_map1_iso).signature())

    def test_random_small_graphs(self):
        seed = 0
        for _ in range(20):
            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False)
            self.random_small_graph(seed, nodes_map=True, edges_map=False)
            self.random_small_graph(seed, nodes_map=True, edges_map=True)
            self.random_small_graph(seed, nodes_map=False, edges_map=True)

            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, k=5)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, k=5)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, k=5)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, k=5)

            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, p=0.5)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, p=0.5)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, p=0.5)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, p=0.5)

            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, p=0.5, k=5)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, p=0.5, k=5)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, p=0.5, k=5)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, p=0.5, k=5)


    def test_random_small_directed_graphs(self):
        seed = 0
        for _ in range(20):
            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, is_directed=True)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, is_directed=True)

            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, k=5, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, k=5, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, k=5, is_directed=True)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, k=5, is_directed=True)

            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, p=0.5, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, p=0.5, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, p=0.5, is_directed=True)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, p=0.5, is_directed=True)

            seed += 1
            self.random_small_graph(seed, nodes_map=False, edges_map=False, p=0.5, k=5, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=False, p=0.5, k=5, is_directed=True)
            self.random_small_graph(seed, nodes_map=True, edges_map=True, p=0.5, k=5, is_directed=True)
            self.random_small_graph(seed, nodes_map=False, edges_map=True, p=0.5, k=5, is_directed=True)


    def test_sign(self):
        n = 1000  # Number of nodes
        p = 0.002 # Probability of edge

        np.random.seed(42)
        G1 = random_graph(n, p)

        iso_lab = IsomorphismLab(G1)
        G2, _, _ = iso_lab.isomorphic_copy()  # isomorphic copy

        G3 = random_graph(n, p) # other random graph

        sig = iso_lab.signature()

        self.assertTrue(sig == IsomorphismLab(G2).signature()) # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab(G3).signature()) # signature different for non isometric graphs

    def test_coloured_sign(self):
        n = 1000  # Number of nodes
        p = 0.002  # Probability of edge

        np.random.seed(43)
        G1 = random_graph(n, p)

        color_map = random_color_map(G1, k=3)

        iso_lab = IsomorphismLab(G1, nodes_color_map=color_map)
        G2, iso_color_map, _ = iso_lab.isomorphic_copy()  # isomorphic copy

        G3 = random_graph(n, p)  # other random graph

        sig = iso_lab.signature()

        self.assertTrue(sig == IsomorphismLab(G2, nodes_color_map=iso_color_map).signature())  # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab(G3, nodes_color_map=random_color_map(G3, k=3)).signature())  # signature different for non isometric graphs
        self.assertFalse(sig == IsomorphismLab(G2, nodes_color_map=random_color_map(G2, k=3)).signature())  # signature different for isometric graph but with different colors

    def test_coloured_not_whole_graph_sign(self):
        n = 1000  # Number of nodes
        p = 0.002  # Probability of edge

        np.random.seed(43)
        G1 = random_graph(n, p)

        color_map = random_color_map(G1, k=3, p=0.5)

        iso_lab = IsomorphismLab(G1, nodes_color_map=color_map)
        G2, iso_color_map, _ = iso_lab.isomorphic_copy()  # isomorphic copy

        G3 = random_graph(n, p)  # other random graph

        sig = iso_lab.signature()

        self.assertTrue(sig == IsomorphismLab(G2, nodes_color_map=iso_color_map).signature())  # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab(G3, nodes_color_map=random_color_map(G3, k=3)).signature())  # signature different for non isometric graphs
        self.assertFalse(sig == IsomorphismLab(G2, nodes_color_map=random_color_map(G2, k=3)).signature())  # signature different for isometric graph but with different colors

    def test_coloured_not_whole_graph_edges_sign(self):
        n = 1000  # Number of nodes
        p = 0.002  # Probability of edge

        np.random.seed(43)
        G1 = random_graph(n, p)

        color_map = random_color_map(G1, k=3, p=0.5)
        edges_color_map = random_edges_color_map(G1, k=3, p=0.5)

        iso_lab = IsomorphismLab(G1, nodes_color_map=color_map, edges_color_map=edges_color_map)
        G2, iso_color_map, iso_edges_color_map = iso_lab.isomorphic_copy()  # isomorphic copy

        G3 = random_graph(n, p)  # other random graph

        sig = iso_lab.signature()

        self.assertTrue(sig == IsomorphismLab(G2, nodes_color_map=iso_color_map, edges_color_map=iso_edges_color_map).signature())  # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab(G3, nodes_color_map=random_color_map(G3, k=3, p=0.5), edges_color_map=random_edges_color_map(G3, k=3, p=0.5)).signature())  # signature different for non isometric graphs
        self.assertFalse(sig == IsomorphismLab(G2, nodes_color_map=iso_color_map, edges_color_map=random_edges_color_map(G3, k=3, p=0.5)).signature())  # signature different for isometric graph but with different colors


    def test_example_1(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        G.add_node(3)
        G.add_node(4)
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])

        node_color_map = {1: "red", 2: "blue", 3: "red", 4: "blue"}
        node_color_map_zero = {1: "null", 2: "null", 3: "null", 4: "null"}
        edges_color_map1 = {(1, 2): "white", (2, 3): "white", (1, 4): "black", (4, 3): "black"}
        edges_color_map2 = {(1, 2): "white", (2, 3): "black", (1, 4): "white", (4, 3): "black"}

        sig1 = IsomorphismLab(G, nodes_color_map=node_color_map, edges_color_map=edges_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=node_color_map, edges_color_map=edges_color_map2).signature()

        self.assertNotEqual(sig1, sig2)

        sig1 = IsomorphismLab(G, nodes_color_map=node_color_map_zero, edges_color_map=edges_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=node_color_map_zero, edges_color_map=edges_color_map2).signature()

        self.assertEqual(sig1, sig2)

        sig1 = IsomorphismLab(G, edges_color_map=edges_color_map1).signature()
        sig2 = IsomorphismLab(G, edges_color_map=edges_color_map2).signature()

        self.assertEqual(sig1, sig2)


    def test_example_2(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        G.add_node(3)
        G.add_node(4)
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])

        node_color_map1 = {3: "white"}
        node_color_map2 = {2: "white"}
        node_color_map3 = {1: "white"}
        node_color_map4 = {1: "black", 2: "black", 3: "white", 4: "black"}
        node_color_map5 = {1: "black", 2: "white", 3: "black", 4: "black"}

        sig1 = IsomorphismLab(G, nodes_color_map=node_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=node_color_map2).signature()
        sig3 = IsomorphismLab(G, nodes_color_map=node_color_map3).signature()

        self.assertEqual(sig1, sig2)
        self.assertNotEqual(sig1, sig3)

        sig4 = IsomorphismLab(G, nodes_color_map=node_color_map4).signature()
        sig5 = IsomorphismLab(G, nodes_color_map=node_color_map5).signature()

        self.assertEqual(sig4, sig5)

        G2 = nx.Graph()
        G2.add_nodes_from(G.nodes)
        G2.add_edges_from(G.edges)
        G2.add_edge(4, 1)

        sig1 = IsomorphismLab(G).signature()
        sig2 = IsomorphismLab(G2).signature()

        self.assertNotEqual(sig1, sig2)


    def test_example_3(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        G.add_node(3)
        G.add_node(4)
        G.add_node(5)
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)])

        nodes_color_map1 = {1: "white"}
        nodes_color_map2 = {2: "white"}
        edges_color_map1 = {(2, 3): "red"}
        edges_color_map2 = {(2, 1): "red"}

        sig1 = IsomorphismLab(G, nodes_color_map=nodes_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=nodes_color_map2).signature()

        self.assertEqual(sig1, sig2)

        sig1 = IsomorphismLab(G, nodes_color_map=nodes_color_map2, edges_color_map=edges_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=nodes_color_map2, edges_color_map=edges_color_map2).signature()

        self.assertEqual(sig1, sig2)


    def test_example_4(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        G.add_node(3)
        G.add_node(4)
        G.add_node(5)
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5)])

        nodes_color_map1 = {1: "white"}
        nodes_color_map2 = {2: "white"}
        edges_color_map1 = {(2, 3): "red"}
        edges_color_map2 = {(2, 1): "red"}

        sig1 = IsomorphismLab(G, nodes_color_map=nodes_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=nodes_color_map2).signature()

        self.assertNotEqual(sig1, sig2)

        sig1 = IsomorphismLab(G, nodes_color_map=nodes_color_map1, edges_color_map=edges_color_map1).signature()
        sig2 = IsomorphismLab(G, nodes_color_map=nodes_color_map1, edges_color_map=edges_color_map2).signature()

        self.assertNotEqual(sig1, sig2)


