import unittest

import networkx as nx
import numpy as np

from reason.tools.graph import IsomorphismLab

class TestSignature(unittest.TestCase):
    def test_sign(self):
        n = 1000  # Number of nodes
        p = 0.002 # Probability of edge

        np.random.seed(42)
        binary_matrix = (np.random.rand(n, n) < p).astype(int)

        G1 = nx.from_numpy_array(binary_matrix)
        G2 = IsomorphismLab.isomorphic_copy(G1)  # isomorphic copy

        binary_matrix = (np.random.rand(n, n) < p).astype(int)
        G3 = nx.from_numpy_array(binary_matrix) # other random graph

        sig = IsomorphismLab.signature(G1)

        self.assertTrue(sig == IsomorphismLab.signature(G2)) # signatures equal for isomorphic graphs
        self.assertFalse(sig == IsomorphismLab.signature(G3)) # signature different for non isometric graphs