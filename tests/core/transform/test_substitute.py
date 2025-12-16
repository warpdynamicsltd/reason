import unittest

from reason.core.language import Language
from reason.core.transform.substitute import (
    NotAdmissibleError,
    substitute_predicate,
)

L = Language()


class TestSubstitutePredicate(unittest.TestCase):
    """Tests for substitute_predicate function."""

    def test_simple_predicate_substitution(self):
        """Test substituting a simple predicate."""
        # Replace P(x) with Q(x) in P(a)
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("P(a)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("Q(a)")
        self.assertEqual(result, expected)

    def test_predicate_with_multiple_args(self):
        """Test substituting predicate with multiple arguments."""
        # Replace P(x, y) with Q(x, y) in P(a, b)
        pattern = L("P(x, y)")
        replacement = L("Q(x, y)")
        formula = L("P(a, b)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("Q(a, b)")
        self.assertEqual(result, expected)

    def test_predicate_substitution_with_formula(self):
        """Test substituting predicate with a complex formula."""
        # Replace P(x) with Q(x) & R(x) in P(a)
        pattern = L("P(x)")
        replacement = L("Q(x) ∧ R(x)")
        formula = L("P(a)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("Q(a) ∧ R(a)")
        self.assertEqual(result, expected)

    def test_no_matching_predicate(self):
        """Test that non-matching predicates are unchanged."""
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("R(a)")
        result = substitute_predicate(pattern, replacement, formula)
        self.assertEqual(result, formula)

    def test_predicate_name_mismatch(self):
        """Test that predicate with different name is not substituted."""
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("R(a)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("R(a)")
        self.assertEqual(result, expected)

    def test_predicate_arity_mismatch(self):
        """Test that predicate with different arity is not substituted."""
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("P(a, b)")
        result = substitute_predicate(pattern, replacement, formula)
        self.assertEqual(result, formula)

    def test_substitution_in_connective(self):
        """Test predicate substitution within connectives."""
        # Replace P(x) with Q(x) in P(a) & P(b)
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("P(a) ∧ P(b)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("Q(a) ∧ Q(b)")
        self.assertEqual(result, expected)

    def test_substitution_under_quantifier(self):
        """Test predicate substitution under quantifier without capture."""
        # Replace P(x, y) with Q(x, y) in ∀z. P(z, a)
        pattern = L("P(x, y)")
        replacement = L("Q(x, y)")
        formula = L("∀z. P(z, a)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("∀z. Q(z, a)")
        self.assertEqual(result, expected)

    def test_variable_capture_prevention(self):
        """Test that variable capture is detected and raises error."""
        # Replace P(x) with Q(y) in ∀y. P(a)
        # This should fail because free variable y in replacement would be captured
        pattern = L("P(x)")
        replacement = L("Q(y)")
        formula = L("∀y. P(a)")
        with self.assertRaises(NotAdmissibleError):
            substitute_predicate(pattern, replacement, formula)

    def test_pattern_variable_not_captured(self):
        """Test that pattern variables are not considered for capture."""
        # Replace P(y) with Q(y) in ∀x. P(x)
        # This is OK because the free y in replacement comes from the pattern
        # and gets mapped to the constant x (not the bound variable x)
        pattern = L("P(y)")
        replacement = L("Q(y)")
        formula = L("∀x. P(x)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("∀x. Q(x)")
        self.assertEqual(result, expected)

    def test_substitution_with_function_terms(self):
        """Test predicate substitution with function terms."""
        # Replace P(x, y) with R(x, y) in P(f(a), g(b, c))
        pattern = L("P(x, y)")
        replacement = L("R(x, y)")
        formula = L("P(f(a), g(b, c))")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("R(f(a), g(b, c))")
        self.assertEqual(result, expected)

    def test_multiple_occurrences(self):
        """Test that all matching occurrences are substituted."""
        # Replace P(x) with Q(x) in P(a) => (P(b) & P(c))
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("P(a) → (P(b) ∧ P(c))")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("Q(a) → (Q(b) ∧ Q(c))")
        self.assertEqual(result, expected)

    def test_invalid_pattern_not_predicate(self):
        """Test that non-predicate pattern raises error."""
        pattern = L("P(x) ∧ Q(y)")
        replacement = L("R(x)")
        formula = L("P(a)")
        with self.assertRaises(NotAdmissibleError):
            substitute_predicate(pattern, replacement, formula)

    # def test_invalid_pattern_with_non_variable(self):
    #     """Test that pattern with non-variable argument raises error."""
    #     pattern = L("P(a)")
    #     replacement = L("Q(a)")
    #     formula = L("P(a)")
    #     with self.assertRaises(NotAdmissibleError):
    #         substitute_predicate(pattern, replacement, formula)

    def test_nested_quantifiers_no_capture(self):
        """Test substitution with nested quantifiers without capture."""
        # Replace P(x) with Q(x, z) in ∀y. ∃z. P(y)
        # z is bound so this should succeed if z in Q(x, z) gets substituted
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("∀x. ∃y. P(y)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("∀x. ∃y. Q(y)")
        self.assertEqual(result, expected)

    def test_complex_replacement_formula(self):
        """Test substitution with complex replacement formula."""
        # Replace P(x) with (Q(x) → R(x)) ∨ S(x)
        pattern = L("P(x)")
        replacement = L("(Q(x) → R(x)) ∨ S(x)")
        formula = L("P(a) ∧ P(b)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("((Q(a) → R(a)) ∨ S(a)) ∧ ((Q(b) → R(b)) ∨ S(b))")
        self.assertEqual(result, expected)

    def test_substitution_preserves_other_predicates(self):
        """Test that non-matching predicates are preserved."""
        # Replace P(x) with Q(x) in P(a) ∧ R(b) ∧ P(c)
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("P(a) ∧ R(b) ∧ P(c)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("Q(a) ∧ R(b) ∧ Q(c)")
        self.assertEqual(result, expected)

    def test_substitution_with_nested_connectives(self):
        """Test substitution in deeply nested formula."""
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("(P(a) → P(b)) → (P(c) ∨ P(d))")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("(Q(a) → Q(b)) → (Q(c) ∨ Q(d))")
        self.assertEqual(result, expected)

    def test_substitution_with_quantified_replacement(self):
        """Test substitution when replacement contains quantifiers."""
        # Replace P(x) with ∀y. Q(x, y)
        pattern = L("P(x)")
        replacement = L("∀y. Q(x, y)")
        formula = L("P(a)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("∀y. Q(a, y)")
        self.assertEqual(result, expected)

    def test_capture_check_with_quantified_replacement(self):
        """Test that capture is detected when replacement has free vars."""
        # Replace P(x) with Q(x, y) where y is free, in ∀y. P(a)
        # Should fail because y in replacement would be captured
        pattern = L("P(x)")
        replacement = L("Q(x, y)")
        formula = L("∀y. P(a)")
        with self.assertRaises(NotAdmissibleError):
            substitute_predicate(pattern, replacement, formula)

    def test_no_capture_when_replacement_var_from_pattern(self):
        """Test no capture error when replacement vars come from pattern."""
        # Replace P(x, y) with Q(x, y) in ∀x. P(a, x)
        # x and y in Q(x, y) come from pattern, so the bound x shouldn't cause issues
        pattern = L("P(x, y)")
        replacement = L("Q(x, y)")
        formula = L("∀z. P(a, z)")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("∀z. Q(a, z)")
        self.assertEqual(result, expected)

    def test_substitution_empty_formula(self):
        """Test substitution in a formula with no matching predicates."""
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("R(a) ∧ S(b)")
        result = substitute_predicate(pattern, replacement, formula)
        self.assertEqual(result, formula)

    def test_substitution_with_implication_and_quantifier(self):
        """Test complex case with implication and quantifiers."""
        # Replace P(x) with Q(x) in ∀y. (P(y) → ∃z. P(z))
        pattern = L("P(x)")
        replacement = L("Q(x)")
        formula = L("∀y. P(y) → (∃z. P(z))")
        result = substitute_predicate(pattern, replacement, formula)
        expected = L("∀y. Q(y) → (∃z. Q(z))")
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()