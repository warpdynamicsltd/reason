import unittest

from reason.core.language import Language
from reason.proofkit.kernel.proof import *

L = Language()


class TestPSURule(unittest.TestCase):
    """Tests for PSU (Predicate Substitution) rule."""

    def test_psu_on_derived_formula(self):
        """Test PSU on a formula derived from axioms (not an assumption)."""
        # We'll use the LEM axiom to get P(a) ∨ ~P(a)
        # Then apply PSU to transform it to Q(a) ∨ ~Q(a)
        BEGIN()
        r1 = LEM(L("P(a)"))  # Derives P(a) ∨ ~P(a)
        self.assertEqual(formula(r1), L("P(a) ∨ ~P(a)"))

        r2 = PSU(r1, L("P(x)"), L("Q(x)"))  # Substitute P with Q
        self.assertEqual(formula(r2), L("Q(a) ∨ ~Q(a)"))

        result = RETURN()
        # The proof derives Q(a) ∨ ~Q(a) without assumptions
        self.assertEqual(result, L("Q(a) ∨ ~Q(a)"))

    def test_psu_on_conjunction_axiom(self):
        """Test PSU on a conjunction derived from AND axiom."""
        BEGIN()
        # Use AND axiom: a → (b → (a ∧ b))
        # With a = P(x), b = P(y), we get: P(x) → (P(y) → (P(x) ∧ P(y)))
        r1 = AND(L("P(x)"), L("P(y)"))
        self.assertEqual(formula(r1), L("P(x) → (P(y) → (P(x) ∧ P(y)))"))

        # Apply PSU to substitute P with Q
        r2 = PSU(r1, L("P(z)"), L("Q(z)"))
        self.assertEqual(formula(r2), L("Q(x) → (Q(y) → (Q(x) ∧ Q(y)))"))

        result = RETURN()
        self.assertEqual(result, L("Q(x) → (Q(y) → (Q(x) ∧ Q(y)))"))

    def test_psu_transforms_implication(self):
        """Test PSU transforming an implication axiom."""
        BEGIN()
        # IMP axiom: a → (b → a)
        # With a = P(x), b = P(y)
        r1 = IMP(L("P(x)"), L("P(y)"))
        self.assertEqual(formula(r1), L("P(x) → (P(y) → P(x))"))

        # Apply PSU to substitute P with Q
        r2 = PSU(r1, L("P(z)"), L("Q(z)"))
        self.assertEqual(formula(r2), L("Q(x) → (Q(y) → Q(x))"))

        result = RETURN()
        self.assertEqual(result, L("Q(x) → (Q(y) → Q(x))"))

    def test_psu_with_complex_replacement(self):
        """Test PSU with a more complex replacement formula."""
        BEGIN()
        # Start with P(a) ∨ ~P(a) from LEM
        r1 = LEM(L("P(a)"))

        # Replace P(x) with (Q(x) ∧ R(x))
        r2 = PSU(r1, L("P(x)"), L("Q(x) ∧ R(x)"))
        # Should get (Q(a) ∧ R(a)) ∨ ~(Q(a) ∧ R(a))
        self.assertEqual(formula(r2), L("(Q(a) ∧ R(a)) ∨ ~(Q(a) ∧ R(a))"))

        result = RETURN()
        self.assertEqual(result, L("(Q(a) ∧ R(a)) ∨ ~(Q(a) ∧ R(a))"))

    def test_psu_preserves_other_predicates(self):
        """Test that PSU only substitutes matching predicates."""
        BEGIN()
        # Use ORL axiom: a → (a ∨ b)
        # With a = P(x), b = R(y)
        r1 = ORL(L("P(x)"), L("R(y)"))
        self.assertEqual(formula(r1), L("P(x) → (P(x) ∨ R(y))"))

        # Substitute only P, leave R unchanged
        r2 = PSU(r1, L("P(z)"), L("Q(z)"))
        self.assertEqual(formula(r2), L("Q(x) → (Q(x) ∨ R(y))"))

        result = RETURN()
        self.assertEqual(result, L("Q(x) → (Q(x) ∨ R(y))"))


if __name__ == "__main__":
    unittest.main()
