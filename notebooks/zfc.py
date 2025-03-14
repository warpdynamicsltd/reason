#%%
from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory

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

#%%
f = ZFC.compile("∀(x) empty(x) → x = ∅")
print(ZFC.prover.run(f, output_axiom_names="on"))

#%%
T = Theory(parser=reason_parser, prover=vampire_prover)
#T.add_const("∅")

f = T.compile("(∀(x) ~(x = o) → (∃(y) y ∈ x ∧ y ∩ x = o)) ∧ (∀e. empty(e) ⟷ (∀(x) ~(x ∈ e))) → (∀(x) empty(x) → x = o)")
print(T.prover.run(f, output_axiom_names="on"))
#print(res)