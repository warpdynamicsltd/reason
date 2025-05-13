import unittest
from collections import deque

from reason.core.theory import Theory
from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.transform.signature import formula_sha256


class TestFormula(unittest.TestCase):
    def test_formula_sha256(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)
        T.add_const("c")

        matches = [
            ("P(x) ∧ Q(y)", "Q(y) ∧ P(x)"),
            ("P(x) ∧ Q(y) ∧ R(z)", "Q(y) ∧ P(x) ∧ R(z)"),
            ("P(x) ∧ Q(y) ∧ R(z)", "R(z) ∧ Q(y) ∧ P(x)"),
            ("P(x) ∧ Q(y) ∧ R(z) ∧ S(t)", "R(z) ∧ S(t) ∧ Q(y) ∧ P(x)"),
            ("P(x) ∧ Q(y) ∧ R(z) ∧ S(t)", "R(z) ∧ (S(t) ∧ Q(y)) ∧ P(x)"),
            ("P(x) ∧ Q(y) ∧ R(z) ∧ S(t)", "(R(z) ∧ S(t)) ∧ (Q(y) ∧ P(x))"),
            ("(∀x. P(x)) ∧ (∀y. Q(y)) ∧ (∀z. R(z))", "(∀z. R(z)) ∧ (∀y. Q(y)) ∧ (∀x. P(x))"),
            ("P(c) ∧ Q(y)", "Q(y) ∧ P(c)"),
            ("∀x. P(x) ∧ Q(y)", "Q(y) ∧ P(x)"),
            ("P(x) ∧ Q(y)", "∀y. Q(y) ∧ P(x)"),
            ("∀x. ∀y. P(x) ∨ Q(y)", "Q(y) ∨ P(x)"),
            ("P(x) ∨ Q(y)", "Q(y) ∨ P(x)"),
            ("P(x) ∨ Q(y) ∨ R(z)", "Q(y) ∨ P(x) ∨ R(z)"),
            ("P(x) ∨ Q(y) ∨ R(z)", "R(z) ∨ Q(y) ∨ P(x)"),
            ("(∀x. P(x)) ∨ (∀y. Q(y)) ∨ (∀z. R(z))", "(∀z. R(z)) ∨ (∀y. Q(y)) ∨ (∀x. P(x))"),
            ("∀x. P(x) ∨ Q(y)", "Q(y) ∨ P(x)"),
            ("P(x) ∨ Q(y)", "∀y. Q(y) ∨ P(x)"),
            ("∀x. ∀y. P(x) ∨ Q(y)", "Q(y) ∨ P(x)"),
            ("P(x) ⟷ Q(y)", "Q(y) ⟷ P(x)"),
            ("∀x. P(x) ⟷ Q(y)", "Q(y) ⟷ P(x)"),
            ("P(x) ⟷ Q(y)", "∀y. Q(y) ⟷ P(x)"),
            ("f(x) = g(x)", "g(x) = f(x)"),
            ("f(x) = g(x)", "g(a) = f(a)"),
            ("∃x. ∀z. P(x) ∧ Q(z)", "∃x. ∀y. Q(y) ∧ P(x)"),
            ("∃x. ∀z. P(x) ∨ Q(z)", "∃x. ∀y. Q(y) ∨ P(x)"),
            ("a = b ⟷ (∀y. P(y, a, b))", "b = a ⟷ (∀y. P(y, a, b))"),
            ("a = b ⟷ (∀y. P(y, a, b))", "(∀y. P(y, a, b)) ⟷ a = b"),
            ("b = a ⟷ (∀y. P(y, a, b))", "(∀y. P(y, a, b)) ⟷ a = b"),
            ("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", "∀x.∀y. x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)"),
            ("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", "∀x.∀y. y = x ⟷ (∀(z) z ∈ x ⟷ z ∈ y)"),
            ("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", "∀x.∀y. x = y ⟷ (∀(z) z ∈ y ⟷ z ∈ x)"),
            ("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", "∀x.∀y. (∀(z) z ∈ y ⟷ z ∈ x) ⟷ x = y"),
            ("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", "∀y.∀x. (∀(z) z ∈ y ⟷ z ∈ x) ⟷ x = y")
        ]

        for t1, t2 in matches:
            f1 = T.compile(t1)
            f2 = T.compile(t2)

            self.assertEqual(formula_sha256(f1), formula_sha256(f2))


    def test_formula_no_match_sha256(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)
        T.add_const("c")

        matches = [
            ("P(x) ∧ Q(y)", "Q(c) ∧ P(x)")
        ]

        for t1, t2 in matches:
            f1 = T.compile(t1)
            f2 = T.compile(t2)

            self.assertNotEqual(formula_sha256(f1), formula_sha256(f2))
