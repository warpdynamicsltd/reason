import unittest

import networkx as nx
import numpy as np

from reason.tools.graph.gen import random_graph
from reason.tools.graph import IsomorphismLab

class TestSignature(unittest.TestCase):
    def test_sign(self):
        n = 1000  # Number of nodes
        p = 0.002 # Probability of edge

        np.random.seed(42)
        G1 = random_graph(n, p)

        iso_lab = IsomorphismLab(G1)
        G2 = iso_lab.isomorphic_copy()  # isomorphic copy

        G3 = random_graph(n, p) # other random graph

        sig = iso_lab.signature()

        self.assertTrue(sig == IsomorphismLab(G2).signature()) # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab(G3).signature()) # signature different for non isometric graphs