import networkx as nx
import numpy as np


def random_graph(n, p):
    binary_matrix = (np.random.rand(n, n) < p).astype(int)
    np.fill_diagonal(binary_matrix, 0)
    binary_matrix = np.maximum(binary_matrix, binary_matrix.T)
    return nx.from_numpy_array(binary_matrix)
