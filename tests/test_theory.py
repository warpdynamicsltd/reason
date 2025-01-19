import unittest

from reason.vampire import Vampire
from reason.parser import Parser

from reason.core.theory import Theory

class TestParser(unittest.TestCase):
  def test_zfc_simple(self):
    parser = Parser()
    vampire_prover = Vampire()

    ZFC = Theory(parser, vampire_prover)

    ZFC.add_const("∅")

    ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
    ZFC.add_axiom("∀(x) ~(x ∈ ∅)", name="a1")
    ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
    ZFC.add_axiom("∀(x, z) z ∈ s(x) ⟷ z = x", name="a3")
    ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name='a4')
    ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name='a5')

    self.assertTrue(ZFC("∀(x, y) empty(x) ∧ empty(y) → x = y"))
    self.assertTrue(ZFC("empty(x) → x = ∅"))
    self.assertTrue(ZFC("s(x) = s(y) → x = y"))
    self.assertTrue(ZFC("∀(x, y, z) z = s(x) ∪ s(y) → x ∈ z ∧ y ∈ z"))


