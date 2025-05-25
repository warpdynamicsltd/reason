import unittest
from collections import deque

from reason.core.theory_v1 import Theory_v1
from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.transform.skolem import skolem_sha256


class TestSkolem(unittest.TestCase):
  def test_skolem_sha256(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory_v1(parser, vampire_prover)
        T.add_const("c")

        matches = [
            ("P(x) ∧ Q(y)", "Q(y) ∧ P(x)"),
            ("∀x. P(x) ∧ Q(y)", "Q(y) ∧ P(x)"),
            ("P(x) ∧ Q(y)", "∀y. Q(y) ∧ P(x)"),
            ("∀x. ∀y. P(x) ∧ Q(y)", "Q(y) ∧ P(x)"),
            ("f(x) = g(x)", "g(x) = f(x)"),
            ("f(x) = g(x)", "g(a) = f(a)"),
            ("∃x. ∀z. P(x) ∧ Q(z)", "∃x. ∀y. Q(y) ∧ P(x)"),
            ("a = b ⟷ (∀y. P(y, a, b))", "b = a ⟷ (∀y. P(y, a, b))"),
            # ("a = b ⟷ (∀y. P(y, a, b))", "(∀y. P(y, a, b)) ⟷ a = b")
        ]

        for t1, t2 in matches:
            f1 = T.compile(t1)
            f2 = T.compile(t2)

            self.assertEqual(skolem_sha256(f1), skolem_sha256(f2))
