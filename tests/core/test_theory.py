import unittest

from reason.vampire import Vampire
from reason.parser import Parser

from reason.core.theory import Theory


class TestTheory(unittest.TestCase):
    @staticmethod
    def get_ZFC_theory():
        parser = Parser()
        vampire_prover = Vampire()

        ZFC = Theory(parser, vampire_prover, inspect=True)

        ZFC.add_const("∅")

        ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
        ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
        ZFC.add_axiom("empty(∅)", name="a1")
        ZFC.add_axiom(r"∀(x, z) z ∈ {x} ⟷ z = x", name="a3")
        ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name="a4")
        ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name="a5")
        ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name="d2")
        ZFC.add_axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)", name="a6")
        ZFC.add_axiom(r"{a, b} = {a} ∪ {b}", name="d3")
        ZFC.add_axiom(r"(a, b) = {a, {a, b}}", name="d4")

        return ZFC

    def test_zfc_simple(self):
        ZFC = self.get_ZFC_theory()

        self.assertTrue(ZFC("∀(x, y) empty(x) ∧ empty(y) → x = y"))
        self.assertTrue(ZFC("empty(x) → x = ∅"))
        self.assertTrue(ZFC(r"{x} = {y} → x = y"))
        self.assertTrue(ZFC(r"∀(x, y, z) z = {x} ∪ {y} → x ∈ z ∧ y ∈ z"))
        self.assertTrue(ZFC(r"∀(x, y) {x, y} = {x} → x = y"))

    def test_zfc_proof(self):
        ZFC = self.get_ZFC_theory()

        premise = r"~({x} ∩ {y} = ∅)"
        thesis = "x = y"

        proof = r"""{
        ~({x} ∩ {y} = ∅);
        ∃(z){
            z ∈ {x} ∧ z ∈ {y};
            z = x ∧ z = y;
            ∀(k) (k ∈ x ⟷ k ∈ z) ∧ (k ∈ z ⟷ k ∈ y);
            x = y;
        };

    }
    """

        self.assertTrue(ZFC.check_proof(premise, thesis, proof))
