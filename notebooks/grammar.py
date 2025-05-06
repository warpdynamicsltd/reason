#%%
import json
import sys
import json

from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory
from reason.printer import Printer
from reason.core.transform.skolem import skolem_sha256
from reason.core.transform.signature import formula_sha256, signature
from reason.core.fof import conjunction

reason_parser = Parser()
vampire_prover = Vampire()
printer = Printer(reason_parser.ogc)

T = Theory(parser=reason_parser, prover=vampire_prover)

# print(conjunction(T.compile("A(x)"), T.compile("B(x)"), T.compile("C(x)")))
# print(reason_parser.dynamic_code)
# %%

print(printer(T.compile("A({x ∈ z: P(x, {t ∈ z: E(t)})}, {x ∈ b: Q(x)})")))


# %%
