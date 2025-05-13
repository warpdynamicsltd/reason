#%%
import json
import sys
import json

from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory
from reason.core.transform.skolem import skolem_sha256
from reason.core.transform.signature import formula_sha256, signature

reason_parser = Parser()
vampire_prover = Vampire()

ZFC = Theory(parser=reason_parser, prover=vampire_prover, cache_folder_path=".exp1")

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

#ZFC.absorb_cache()

#%%
ZFC.add_const("a")

#%%
ZFC.add_const("p")
ZFC.add_const("q")

ZFC.add_axiom("p = {x ∈ a: P(x)}")
ZFC.add_axiom("q = {x ∈ a: Q(x)}")

#%%
ZFC.provable("∀ k. k ∈ p ∪ q ⟷ k ∈ p ∨ k ∈ q")

#%%
ZFC.provable("∀ k. k ∈ p ∨ k ∈ q ⟷ (k ∈ a ∧ P(k)) ∨ (k ∈ a ∧ Q(k))")

#%%
ZFC.provable("∀ k. k ∈ p ∧ k ∈ q ⟷ (k ∈ a ∧ P(k)) ∧ (k ∈ a ∧ Q(k))")

#%%
ZFC.provable("∀ k. (k ∈ a ∧ P(k)) ∨ (k ∈ a ∧ Q(k)) ⟷ k ∈ a ∧ (P(k) ∨ Q(k))")

#%%
ZFC.provable("∀ k. (k ∈ a ∧ P(k)) ∧ (k ∈ a ∧ Q(k)) ⟷ k ∈ a ∧ (P(k) ∧ Q(k))")
# %%
ZFC.provable("p ∪ q = {x ∈ a: P(x) ∨ Q(x)}")

#%%
ZFC.provable("p ∪ q = {x ∈ a: P(x)} ∪ {x ∈ a: Q(x)}")


# %%
ZFC.provable("p ∩ q = {x ∈ a: P(x) ∧ Q(x)}")

#%%
ZFC.provable("p ∩ q = {x ∈ a: P(x)} ∩ {x ∈ a: Q(x)}")

# %%
ZFC.provable("{u ∈ a: P(u)} ∪ {u ∈ a: Q(u)} = {x ∈ a: P(x) ∨ Q(x)}")


# %%
ZFC.provable("{u ∈ a: P(u)} ∩ {u ∈ a: Q(u)} = {x ∈ a: P(x) ∧ Q(x)}")
# %%
