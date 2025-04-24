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


#%%


from reason.tools.graph import IsomorphismLab

n = 20       # Number of nodes
p = 0.2      # Probability for edge creation

G1, G2 = random_non_iso_connected_graphs(n, is_directed=True)

colors = random.choices(["0", "1"], k=n)
color_map = {k: colors[i] for i, k in enumerate(G1.nodes())}

#print("components", nx.number_connected_components(G1))
iso_lab1 = IsomorphismLab(G1, nodes_color_map=color_map)

nx.draw(G1, with_labels=True, node_color='skyblue', alpha=0.5)
plt.show()

nx.draw(G2, with_labels=True, node_color='skyblue', alpha=0.5)
plt.show()



#%%
G2, iso_color_map, iso_edges_map = iso_lab1.isomorphic_copy()

G3 = random_graph(n)

# Draw the generated graph
# nx.draw(G1 , node_color='skyblue', alpha=0.5)
# plt.show()
#
# nx.draw(G2 , node_color='skyblue', alpha=0.5)
# plt.show()

nx.draw(G1, with_labels=True, node_color='skyblue', alpha=0.5)
plt.show()
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


