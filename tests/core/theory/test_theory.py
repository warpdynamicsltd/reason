import unittest
import logging
from reason.core.theory.zfc import ZFC
from reason.core.theory.context import Context

class TestZFCTheory(unittest.TestCase):
    def test_zfc_root_proof(self):
        zfc = ZFC()

        # BEGIN OF AXIOMS
        zfc.axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)")
        zfc.axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))")
        zfc.axiom("empty(∅)")
        zfc.axiom("∀(x, z) z ∈ {x} ⟷ z = x")
        zfc.axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y")
        zfc.axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y")
        zfc.axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)")
        zfc.axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)")
        # END OF AXIOMS

        zfc.add("{a, b} = {a} ∪ {b}")
        zfc.add("{a, b, c} = {a} ∪ {b} ∪ {c}")
        zfc.add("(a, b) = {a, {a, b}}")

        #%%
        zfc._add_const("_a")
        zfc._add_const("_b")
        zfc._add_const("_c")
        # zfc._add_const("k")

        #%%
        zfc.add("k ∈ _a ∩ (_b ∪ _c) ⟷ k ∈ (_a ∩ _b) ∪ (_a ∩ _c)")
        #%%
        zfc.add("_a ∩ (_b ∪ _c) = (_a ∩ _b) ∪ (_a ∩ _c)")


    def test_zfc_context_proof(self):
        zfc = ZFC()
        # BEGIN OF AXIOMS
        zfc.axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)")
        zfc.axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))")
        zfc.axiom("empty(∅)")
        zfc.axiom("∀(x, z) z ∈ {x} ⟷ z = x")
        zfc.axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y")
        zfc.axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y")
        zfc.axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)")
        zfc.axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)")
        # END OF AXIOMS

        zfc.add("{a, b} = {a} ∪ {b}")
        zfc.add("{a, b, c} = {a} ∪ {b} ∪ {c}")
        zfc.add("(a, b) = {a, {a, b}}")

        with Context(zfc) as c1:
            c1.declare("a")
            c1.declare("b")
            c1.declare("c")
            c1.declare("p")
            c1.declare("q")

            c1.assume("p = a ∩ (b ∪ c)")
            c1.assume("q = (a ∩ b) ∪ (a ∩ c)")

            with c1.open_context() as c2:
                c2.declare("k")
                c2.assume("k ∈ p")
                c2.add("k ∈ a ∩ (b ∪ c)")
                c2.add("k ∈ a ∧ k ∈ (b ∪ c)")
                c2.add("k ∈ a ∧ (k ∈ b ∨ k ∈ c)")
                c2.add("(k ∈ a ∧ k ∈ b) ∨ (k ∈ a ∧ k ∈ c)")
                c2.add("k ∈ (a ∩ b) ∪ (a ∩ c)")
                c2.conclude("k ∈ q")

            with c1.open_context() as c3:
                c3.declare("k")
                c3.assume("k ∈ q")
                c3.add("k ∈ (a ∩ b) ∪ (a ∩ c)")
                c3.add("(k ∈ a ∧ k ∈ b) ∨ (k ∈ a ∧ k ∈ c)")
                c3.add("k ∈ a ∧ (k ∈ b ∨ k ∈ c)")
                c3.add("k ∈ a ∧ k ∈ (b ∪ c)")
                c3.add("k ∈ a ∩ (b ∪ c)")
                c3.conclude("k ∈ p")

            c1.conclude("p = q")

        zfc.add("a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)")