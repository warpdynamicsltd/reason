#%%
import json
import sys

from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory
from reason.core.transform.skolem import skolem_sha256

reason_parser = Parser()
vampire_prover = Vampire()

ZFC = Theory(parser=reason_parser, prover=vampire_prover)

ZFC.add_const("∅")

ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
ZFC.add_axiom("empty(∅)", name="a1")
ZFC.add_axiom("∀(x, z) z ∈ {x} ⟷ z = x", name="a3")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name="a4")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name="a5")
ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name="d2")
ZFC.add_axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)", name="a6")
ZFC.add_axiom("{a, b} = {a} ∪ {b}", name="d3")
ZFC.add_axiom("(a, b) = {a, {a, b}}", name="d4")

ZFC.add_axiom("(a, b, c) = ((a, b), c)", name="d5")


f = ZFC.compile("(a, b) = (c, d) → a = c ∧ b = d")
# print(ZFC.prover.run(f, output_axiom_names="on"))

# proof = ZFC.prove(f)
# if proof is not None:
#     json.dump(proof, sys.stdout, indent=2)

#%%
f = ZFC.compile("(a, b) = (c, d) → b = d ∧ c = a")
print(skolem_sha256(f))

#%%
T = Theory(parser=reason_parser, prover=vampire_prover)
#T.add_const("∅")


#%%
T("(a, b) = (c, d) → a = c ∧ b = d")

#%%
f = ZFC.compile("(a, b) = (c, d) → a = c ∧ b = d")
# print(ZFC.prover.run(f, output_axiom_names="on"))

print(ZFC.prove(f))

#%%
premise = "(a, b, c) = (x, x, x)"
thesis = "a = b"

proof = """{
    (a, b, c) = (x, x, x);
    ∃z. {
      z = (a, b, c);
      z = ((a, b), c);
      z = (x, x, x);
      z = ((x, x), x);
      ((a, b), c) = ((x, x), x);
      (a, b) = (x, x);
      a = x ∧ b = x;
      a = b}
    }
"""

# proof = """{
#     (a, b, c) = (x, x, x);
#     ((a, b), c) = ((x, x), x);
#     ((a, b), c) = ((x, x), x) → (a, b) = (x, x) ∧ c = x;
#     (a, b) = (x, x);
#     (a, b) = (x, x) → a = x ∧ b = x;
#     a = x ∧ b = x;
#     a = b;
# }
# """

print(ZFC.check_proof(premise, thesis, proof))

#%%
ZFC("(a, b, c) = ((a, b), c)")