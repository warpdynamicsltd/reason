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
        G2 = IsomorphismLab.isomorphic_copy(G1)  # isomorphic copy

        G3 = random_graph(n, p) # other random graph

        sig = IsomorphismLab.signature(G1)

        self.assertTrue(sig == IsomorphismLab.signature(G2)) # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab.signature(G3)) # signature different for non isometric graphs