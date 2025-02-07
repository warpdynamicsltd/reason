import unittest

import random
import numpy as np

from reason.tools.graph.gen import random_graph
from reason.tools.graph import IsomorphismLab

def random_color_map(graph, k=2):
    return {n: random.choice(range(k)) for i, n in enumerate(graph.nodes())}

class TestSignature(unittest.TestCase):
    def test_sign(self):
        n = 1000  # Number of nodes
        p = 0.002 # Probability of edge

        np.random.seed(42)
        G1 = random_graph(n, p)

        iso_lab = IsomorphismLab(G1)
        G2, _ = iso_lab.isomorphic_copy()  # isomorphic copy

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

        iso_lab = IsomorphismLab(G1, color_map=color_map)
        G2, iso_color_map = iso_lab.isomorphic_copy()  # isomorphic copy

        G3 = random_graph(n, p)  # other random graph

        sig = iso_lab.signature()

        self.assertTrue(sig == IsomorphismLab(G2, color_map=iso_color_map).signature())  # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab(G3, color_map=random_color_map(G3, k=3)).signature())  # signature different for non isometric graphs
        self.assertFalse(sig == IsomorphismLab(G2, color_map=random_color_map(G2, k=3)).signature())  # signature different for isometric graph but with different colors