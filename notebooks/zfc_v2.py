#%%
import logging
from reason.core.theory.zfc import ZFC
from reason.core.theory.context import Context

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
# END OF AXIOMS

zfc.add("{a, b} = {a} ∪ {b}")
zfc.add("{a, b, c} = {a} ∪ {b} ∪ {c}")
zfc.add("(a, b) = {a, {a, b}}")

#%%
with Context(zfc) as c1:
    c1.declare("a")
    c1.declare("b")
    c1.declare("c")
    c1.declare("p")
    c1.declare("q")

    c1.when("p = a ∩ (b ∪ c)")
    c1.when("q = (a ∩ b) ∪ (a ∩ c)")

    with c1.open_context() as c2:
        c2.declare("k")
        c2.when("k ∈ p")
        c2.then("k ∈ a ∩ (b ∪ c)")
        c2.then("k ∈ a ∧ k ∈ (b ∪ c)")
        c2.then("k ∈ a ∧ (k ∈ b ∨ k ∈ c)")
        c2.then("(k ∈ a ∧ k ∈ b) ∨ (k ∈ a ∧ k ∈ c)")
        c2.then("k ∈ (a ∩ b) ∪ (a ∩ c)")
        c2.conclude("k ∈ q")

    with c1.open_context() as c3:
        c3.declare("k")
        c3.when("k ∈ q")
        c3.then("k ∈ (a ∩ b) ∪ (a ∩ c)")
        c3.then("(k ∈ a ∧ k ∈ b) ∨ (k ∈ a ∧ k ∈ c)")
        c3.then("k ∈ a ∧ (k ∈ b ∨ k ∈ c)")
        c3.then("k ∈ a ∧ k ∈ (b ∪ c)")
        c3.then("k ∈ a ∩ (b ∪ c)")
        c3.conclude("k ∈ p")

    c1.conclude("p = q")

#%%
zfc.add("a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)")


#%%
zfc._add_const("_a")
zfc._add_const("_b")
zfc._add_const("_c")
# zfc._add_const("k")

#%%
zfc.add("k ∈ _a ∩ (_b ∪ _c) ⟷ k ∈ _a ∧ k ∈ (_b ∪ _c)")
#%%
zfc.add("k ∈ _a ∩ (_b ∪ _c) ⟷ k ∈ _a ∧ (k ∈ _b  ∨ k ∈_c)")
#%%
zfc.add("k ∈ _a ∩ (_b ∪ _c) ⟷ (k ∈ _a ∧ k ∈ _b) ∨ (k ∈ _a ∧ k ∈_c)")

#%%
zfc.add("k ∈ _a ∩ (_b ∪ _c) ⟷ k ∈ (_a ∩ _b) ∪ (_a ∩ _c)")
#%%
zfc.add("_a ∩ (_b ∪ _c) = (_a ∩ _b) ∪ (_a ∩ _c)")


#%%
zfc.add("a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)")

#%%
zfc.add("_a = _b")


#%%
zfc.add("(a, b) = (x, y) → a = x ∧ b = y")

#%%
zfc.add("{a, b, c} ∩ {b, c} = {b, c}")


# %%
zfc.add("(a, b) = (x, x) → a = b")
# %%

#%%
zfc.add("{a, a} = {a}")

# %%
zfc.add("{a, a, a} = {a}")
# %%

# %%
zfc.add("{a, a, b} = {a, b}")

# %%
zfc.add("{a, b} = {b, a}")
# %%

zfc.add("(a, b, c) = (a, (b, c))")
# %%
zfc.add("(a, b, c) = (x, y, z) → a = x ∧ b = y ∧ c = z")

# %%
