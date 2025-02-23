#%%
from reason.vampire import Vampire
from reason.parser import Parser
from reason.printer import Printer
from reason.core.theory import Theory
from reason.core.fof import LogicConnective
from reason.core.transform.skolem import prenex_normal_raw, prenex_normal, skolem, SkolemUniqueRepr
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    free_variables, closure
from reason.core.transform.graph import FormulaToGraphLab

import networkx as nx
import matplotlib.pyplot as plt

parser = Parser()
printer = Printer(parser.ogc)

vampire_prover = Vampire(verbose=False)
T = Theory(parser, vampire_prover)

f = T.compile("P(f(x, y), g(x, y))")
G = FormulaToGraphLab(f).graph

node_labels = {n: f"{n}, {G.nodes[n]["arg_idx"] if "arg_idx" in G.nodes[n]['type'] else ""}" for n in G.nodes}

nx.draw(G, labels=node_labels, with_labels=True, node_color='skyblue', alpha=0.5)
plt.show()