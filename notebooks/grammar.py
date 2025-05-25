#%%
import json
import sys
import json

from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory_v1 import Theory_v1
from reason.printer import Printer
from reason.core.transform.skolem import skolem_sha256
from reason.core.transform.signature import formula_sha256, signature
from reason.core.transform.base import conjunction
from reason.core.fof import FormulaBuilder
from reason.core.transform.explode_conj import explode_over_conjunctions

reason_parser = Parser()
vampire_prover = Vampire()
printer = Printer(reason_parser.ogc)

T = Theory_v1(parser=reason_parser, prover=vampire_prover)

#%%
fb = FormulaBuilder(reason_parser("A({x ∈ a: B(x, {t ∈ b: C(t)}) ∧ D(x, {t ∈ d: E(t)})})"))
for a in fb.axioms:
  print(printer(a))


#%%
cons = explode_over_conjunctions(reason_parser("""
  {x ∈ b;
  b ⊂ {t ∈ a: P(t)};
  P(x);}                                    
"""))

for ast in cons:
  print(printer(T.to_formula(ast)))

# print(conjunction(T.compile("A(x)"), T.compile("B(x)"), T.compile("C(x)")))
# print(reason_parser.dynamic_code)
# %%
input_list = [
  "(∀k. (P(k) → Q(k))) → {x ∈ z: P(x)} ⊂ {x ∈ z: Q(x)}",
  "A({x ∈ z ∩ y: P(x)})",
  "A({x ∈ z: P(x)})",
  "∀z. A({x ∈ z: P(x)})",
  "A({x ∈ z: ∃k. P(k, x)})",
  "A({x ∈ z: ∃k. P({n ∈ k: B(n)}, x)})",
  "A({x ∈ f(z): P(x)})",
  "A({x ∈ f(a, b): P(x)})",
  "A({x ∈ z: P(x)}, {x ∈ z: Q(x)})",
  "A({x ∈ a: B(x, {t ∈ b: C(t)})})",
  "A({x ∈ a: B(x, {t ∈ b: C(t)}) ∧ D(x, {t ∈ d: E(t)})})",
  "A({x ∈ a: B(x, {t ∈ b: C(t)})}, {x ∈ c: D(x, {t ∈ d: E(t)})})",
  "A({x ∈ z: P(x)}) ∧ B({x ∈ z: Q(x)})",
  "∀z. A({x ∈ z: P(x)}) ∧ B({x ∈ z: Q(x)})"
]

output_list = []
for text in input_list:
  output_list.append((text, printer(T.compile(text))))

print(json.dumps(output_list, indent=2, ensure_ascii=False))


# print(printer(T.compile("A({x ∈ z: P(x, {t ∈ z: E(t)})}, {x ∈ b: Q(x)})")))
# print(printer(T.compile("A({x ∈ z: P(x)})")))


# %%
