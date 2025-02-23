import time
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def nested_len(obj):
    """
    Return the count of all "atomic" elements in `obj`.
    If `obj` is a tuple or list, recursively count elements inside it.
    Otherwise, treat `obj` as a single item.
    """
    if isinstance(obj, (tuple, list)):
        total = 0
        for item in obj:
            total += nested_len(item)
        return total
    else:
        # If not a tuple/list, it's a single item (e.g., int, float, str, etc.)
        return 1

def random_graph(n):
    binary_matrix = (np.random.rand(n, n) < p).astype(int)
    np.fill_diagonal(binary_matrix, 0)
    binary_matrix = np.maximum(binary_matrix, binary_matrix.T)
    return nx.from_numpy_array(binary_matrix)

#%%


from reason.tools.graph import IsomorphismLab

n = 100       # Number of nodes
p = 0.1      # Probability for edge creation

G1 = random_graph(n)

colors = random.choices([0, 1], k=n)
color_map = {n: colors[i] for i, n in enumerate(G1.nodes())}

#%%
print("components", nx.number_connected_components(G1))
iso_lab1 = IsomorphismLab(G1, color_map=color_map)

G2, iso_color_map = iso_lab1.isomorphic_copy()

G3 = random_graph(n)

# Draw the generated graph
# nx.draw(G1 , node_color='skyblue', alpha=0.5)
# plt.show()
#
# nx.draw(G2 , node_color='skyblue', alpha=0.5)
# plt.show()

#nx.draw(G_copy, with_labels=True, node_color='skyblue', alpha=0.5)
#plt.show()
t = time.time()
sig1 = IsomorphismLab(G1, color_map).signature()
print(round(time.time() - t, 3), "secs")

sig2 = IsomorphismLab(G2, iso_color_map).signature()
sig3 = IsomorphismLab(G3, color_map).signature()

# print(sig1)
# print(sig2)

print(nested_len(sig1))
# print("sig1", sig1)
# print("sig2", sig2)
print(sig1 == sig2)
print(sig1 == sig3)


