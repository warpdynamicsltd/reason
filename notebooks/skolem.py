#%%
from reason.vampire import Vampire
from reason.parser import Parser
from reason.printer import Printer
from reason.core.theory import Theory
from reason.core.fof import LogicConnective
from reason.core.transform.skolem import prenex_normal_raw, prenex_normal, skolem, SkolemUniqueRepr, skolem_unique_repr
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    free_variables, closure
from reason.core.transform.graph import FormulaToGraphLab

import networkx as nx
import matplotlib.pyplot as plt

parser = Parser()
printer = Printer(parser.ogc)

vampire_prover = Vampire(verbose=False)
T = Theory(parser, vampire_prover)
T.add_const('c')

#%%

f = T.compile("∀x. ∃y. A(x, y) ∧ B(x, y) → A(x, y)")
# f = T.compile("(∀x. A(x) ∧ B(x)) → (∀x. A(f(x)))")
# f = T.compile("P(c) → P(c)")
print(T.prover.run(f, output_axiom_names="on"))

#%%
s = skolem(f)
print(printer(s))

a1 = T.compile("P(x, y)")
a2 = T.compile("Q(x)")
a3 = T.compile("R(y)")

G = FormulaToGraphLab(skolem_unique_repr(f)).graph

def visualise(n):
    res = f"{G.nodes[n]["type"]}"
    if "arg_idx" in G.nodes[n]:
        res += f", arg_idx={G.nodes[n]["arg_idx"]}"

    return res

node_labels = {n: visualise(n) for n in G.nodes}

# nx.draw_networkx_nodes(G, pos=nx.spring_layout(G), node_color='skyblue', alpha=0.5)
# nx.draw_networkx_edges(G, pos=nx.spring_layout(G), edge_color='skyblue', alpha=0.5)
# plt.show()

# Get the positions of the nodes
pos = nx.spring_layout(G)

# Draw the graph
nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=300, font_size=16)

# Draw node labels
# labels = nx.get_node_attributes(G, 'label')
nx.draw_networkx_labels(G, pos, node_labels, font_size=16, font_color='black')

# Draw edge labels
edge_labels = nx.get_edge_attributes(G, 'arg_idx')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)
plt.show()

#%%
import matplotlib.pyplot as plt

# Sample data
x = [1, 2, 3, 4, 5]
y = [10, 20, 25, 30, 40]

# Create the plot
plt.plot(x, y, marker='o', linestyle='-', color='b', label='Sample Line')

# Add title and labels
plt.title('Sample Plot')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# Add a legend
plt.legend()

# Show the plot
plt.show()
