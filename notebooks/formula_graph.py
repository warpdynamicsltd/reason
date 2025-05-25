#%%
from reason.vampire import Vampire
from reason.parser import Parser
from reason.printer import Printer
from reason.core.theory_v1 import Theory_v1
from reason.core.fof_types import LogicConnective
from reason.core.transform.skolem import prenex_normal_raw, prenex_normal, skolem, SkolemUniqueRepr, skolem_unique_repr
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    free_variables, closure
from reason.core.transform.signature import formula_sha256
from reason.core.transform.graph.skolem import SkolemFormulaToGraphLab
from reason.core.transform.graph.formula import FormulaToGraphLab

import networkx as nx
import matplotlib.pyplot as plt

parser = Parser()
printer = Printer(parser.ogc)

vampire_prover = Vampire(verbose=False)
T = Theory_v1(parser, vampire_prover)
T.add_const('c')

#%%

# f = T.compile("a = b ⟷ (∀y. P(y, a, b))")
f = T.compile("(R(z) ∧ S(t)) ∧ (Q(y) ∧ P(x))")
f2 = T.compile("(∀z. R(z)) ∧ (∀y. Q(y)) ∧ (∀x. P(x))")

ftg = FormulaToGraphLab(f)
ftg2 = FormulaToGraphLab(f2)

print(ftg.signature)

print(formula_sha256(f))
print(formula_sha256(f2))

G = ftg.graph

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=300, font_size=16)
nx.draw_networkx_labels(G, pos, ftg.node_color_map, font_size=16, font_color='black')
nx.draw_networkx_edge_labels(G, pos, edge_labels=ftg.edge_color_map, font_size=12)
plt.show()

G = ftg.get_graph_repr()

nx.write_gexf(G, "g.gefx")

# %%
