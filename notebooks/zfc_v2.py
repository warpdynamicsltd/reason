#%%
import logging
from reason.core.theory.zfc import ZFC

logging.basicConfig(level=logging.INFO)

zfc = ZFC()

# BEGIN OF AXIOMS
zfc.add("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)")
zfc.add("empty(e) ⟷ (∀(x) ~(x ∈ e))")
zfc.add("empty(∅)")
zfc.add("∀(x, z) z ∈ {x} ⟷ z = x")
zfc.add("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y")
zfc.add("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y")
zfc.add("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)")
zfc.add("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)")
zfc.add("{a, b} = {a} ∪ {b}")
zfc.add("{a, b, c} = {a} ∪ {b} ∪ {c}")
zfc.add("(a, b) = {a, {a, b}}")
# END OF AXIOMS

#%%
#zfc.add("(a, b) = (x, y) → a = x ∧ b = y")

zfc.add("{a, b, c} ∩ {b, c} = {b, c}")


# %%
zfc.add("(a, b) = (x, x) → a = b")
# %%
