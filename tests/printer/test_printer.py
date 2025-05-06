import unittest
from reason.core.theory import Theory
from reason.vampire import Vampire
from reason.parser import Parser
from reason.printer import Printer



from reason.parser import Parser

class TestPrinter(unittest.TestCase):
    tests = [
        "P ∧ R ∧ Q",
        "P ∧ (R ∨ Q)",
        "(R ∨ Q) ∧ P",
        "R ∨ Q → P ∧ R",
        "R ∨ Q → ~(P ∧ R)",
        "R ∨ Q → ~~(P ∧ R)",
        "R ∨ (Q → P) ∧ R",
        "R ∨ (∀x. Q(x) → P) ∧ R",
        "R ∨ (∀x. A ∧ (Q(x) → P)) ∧ R",
        "R ∨ (∀x. A ∧ (Q(s(x)) → P)) ∧ R",
        "∀x. ∀u. ∃y. P(x) ∧ (Q(u) ∨ R) → ~(∃z. A(y) ∧ ~B(z))",
        "a ∈ b",
        "∀x. ∀y. x = y ⟷ (∀z. z ∈ x ⟷ z ∈ y)",
        "∀x. ∀y. ∀z. z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y",
        "∀x. ∀y. ∀z. z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y"
    ]
    def test_print(self):
        parser = Parser()
        printer = Printer(parser.ogc)

        vampire_prover = Vampire(verbose=True)
        T = Theory(parser, vampire_prover)

        for text in self.tests:
            f = T.compile(text)
            self.assertEqual(printer(f), text)