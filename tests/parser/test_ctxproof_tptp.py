import unittest

from reason.parser.ctxproof_tptp import CtxProofTPTPParser


class TestCtxProofTPTPParser(unittest.TestCase):
    # Original TPTP tests - should all still work
    tptp_tests = [
        ("![X] : p_A(X)", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Variable(X)))"),
        ("![X] : p_A(f_inc(X))", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Function(inc, Variable(X))))"),
        ("![X, Y, Z] : p_A(f_inc(X), Z, Y)", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(FORALL, Variable(Y), LogicQuantifier(FORALL, Variable(Z), Predicate(A, Function(inc, Variable(X)), Variable(Z), Variable(Y)))))"),
        ("![X] : p_A(X, a)", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Variable(X), Const(a)))"),
        ("![X] : ? [Y] : (p_A(X) & p_B(Y))", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(AND, Predicate(A, Variable(X)), Predicate(B, Variable(Y)))))"),
        ("![X] : ? [Y] : (p_A(X) & ~p_B(Y))", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(AND, Predicate(A, Variable(X)), LogicConnective(NEG, Predicate(B, Variable(Y))))))"),
        ("![X] : ? [Y] : f_A(X) = f_B(Y)", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), Predicate(EQ, Function(A, Variable(X)), Function(B, Variable(Y)))))"),
        ("![X] : ? [Y] : f_A(X) != f_B(Y)", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(NEG, Predicate(EQ, Function(A, Variable(X)), Function(B, Variable(Y))))))"),
        ("![X] : ? [Y] : (p_A(X) | p_B(Y))", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(OR, Predicate(A, Variable(X)), Predicate(B, Variable(Y)))))"),
        ("![X] : ? [Y] : (p_A(X) => p_B(Y))", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(IMP, Predicate(A, Variable(X)), Predicate(B, Variable(Y)))))"),
        ("![X] : ? [Y] : (p_A(X) <=> p_B(Y))", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(IFF, Predicate(A, Variable(X)), Predicate(B, Variable(Y)))))"),
        ("![X] : (? [Y] : (p_A(X) | p_B(Y)))", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(OR, Predicate(A, Variable(X)), Predicate(B, Variable(Y)))))"),
        ("(! [X3] : (p_empty(X3) <=> ! [X0] : ~p_IN(X0,X3)) & ! [X0] : (X0 != X6 => ? [X1] : (f_INTERSECT(X1,X0) = X6 & p_IN(X1,X0)))) => ! [X0] : (p_empty(X0) => X0 = X6)",
         "LogicConnective(IMP, LogicConnective(AND, LogicQuantifier(FORALL, Variable(X3), LogicConnective(IFF, Predicate(empty, Variable(X3)), LogicQuantifier(FORALL, Variable(X0), LogicConnective(NEG, Predicate(IN, Variable(X0), Variable(X3)))))), LogicQuantifier(FORALL, Variable(X0), LogicConnective(IMP, LogicConnective(NEG, Predicate(EQ, Variable(X0), Variable(X6))), LogicQuantifier(EXISTS, Variable(X1), LogicConnective(AND, Predicate(EQ, Function(INTERSECT, Variable(X1), Variable(X0)), Variable(X6)), Predicate(IN, Variable(X1), Variable(X0))))))), LogicQuantifier(FORALL, Variable(X0), LogicConnective(IMP, Predicate(empty, Variable(X0)), Predicate(EQ, Variable(X0), Variable(X6)))))")
    ]

    # Tests for $true and $false predicates
    special_predicate_tests = [
        # $true and $false predicates
        ("$true", "Predicate(TRUE)"),
        ("$false", "Predicate(FALSE)"),
        ("~$true", "LogicConnective(NEG, Predicate(TRUE))"),
        ("~$false", "LogicConnective(NEG, Predicate(FALSE))"),
        ("$true & $false", "LogicConnective(AND, Predicate(TRUE), Predicate(FALSE))"),
        ("$true | $false", "LogicConnective(OR, Predicate(TRUE), Predicate(FALSE))"),
        ("$true => $false", "LogicConnective(IMP, Predicate(TRUE), Predicate(FALSE))"),
        ("$true <=> $false", "LogicConnective(IFF, Predicate(TRUE), Predicate(FALSE))"),
        ("$true => p_A(X)", "LogicConnective(IMP, Predicate(TRUE), Predicate(A, Variable(X)))"),
        ("p_A(X) => $false", "LogicConnective(IMP, Predicate(A, Variable(X)), Predicate(FALSE))"),
        ("![X] : ($true => p_A(X))", "LogicQuantifier(FORALL, Variable(X), LogicConnective(IMP, Predicate(TRUE), Predicate(A, Variable(X))))"),
    ]

    # New tests for Skolem symbols
    skolem_tests = [
        # Skolem constants as terms (converted to skolem_X format)
        ("p_A(sk.1)", "Predicate(A, Const(skolem_1))"),
        ("p_A(sk.23)", "Predicate(A, Const(skolem_23))"),
        ("p_A(sk.1, sk.2)", "Predicate(A, Const(skolem_1), Const(skolem_2))"),

        # Multi-level Skolem constants
        ("p_A(sk.1.2)", "Predicate(A, Const(skolem_1_2))"),
        ("p_A(sk.23.4)", "Predicate(A, Const(skolem_23_4))"),
        ("p_A(sk.2.1.0)", "Predicate(A, Const(skolem_2_1_0))"),

        # Skolem functions with arguments (V_ prefix stripped from variables)
        ("p_A(sk.1(V_X))", "Predicate(A, Function(skolem_1, Variable(X)))"),
        ("p_A(sk.2(V_X, V_Y))", "Predicate(A, Function(skolem_2, Variable(X), Variable(Y)))"),
        ("p_A(sk.1.2(V_X, V_Y, V_Z))", "Predicate(A, Function(skolem_1_2, Variable(X), Variable(Y), Variable(Z)))"),

        # Skolem predicates (nullary)
        ("sk.1", "Predicate(skolem_1)"),
        ("sk.23.4", "Predicate(skolem_23_4)"),

        # Skolem predicates with arguments
        ("sk.1(V_X)", "Predicate(skolem_1, Variable(X))"),
        ("sk.2(V_X, V_Y)", "Predicate(skolem_2, Variable(X), Variable(Y))"),
        ("sk.1.2.3(c_a, c_b, c_c)", "Predicate(skolem_1_2_3, Const(a), Const(b), Const(c))"),

        # Mixed Skolem and regular symbols
        ("p_A(sk.1, c_a)", "Predicate(A, Const(skolem_1), Const(a))"),
        ("p_A(sk.1(V_X), f_B(V_Y))", "Predicate(A, Function(skolem_1, Variable(X)), Function(B, Variable(Y)))"),
        ("p_A(V_X, sk.2(V_Y))", "Predicate(A, Variable(X), Function(skolem_2, Variable(Y)))"),

        # Skolem in equalities
        ("sk.1 = sk.2", "Predicate(EQ, Const(skolem_1), Const(skolem_2))"),
        ("sk.1(V_X) = sk.2(V_Y)", "Predicate(EQ, Function(skolem_1, Variable(X)), Function(skolem_2, Variable(Y)))"),
        ("V_X = sk.1", "Predicate(EQ, Variable(X), Const(skolem_1))"),
        ("sk.1 != V_X", "LogicConnective(NEG, Predicate(EQ, Const(skolem_1), Variable(X)))"),

        # Skolem in logical formulas
        ("p_A(sk.1) & p_B(sk.2)", "LogicConnective(AND, Predicate(A, Const(skolem_1)), Predicate(B, Const(skolem_2)))"),
        ("p_A(sk.1(V_X)) | p_B(V_Y)", "LogicConnective(OR, Predicate(A, Function(skolem_1, Variable(X))), Predicate(B, Variable(Y)))"),
        ("p_A(V_X) => p_B(sk.1)", "LogicConnective(IMP, Predicate(A, Variable(X)), Predicate(B, Const(skolem_1)))"),
        ("~p_A(sk.1)", "LogicConnective(NEG, Predicate(A, Const(skolem_1)))"),

        # Skolem with quantifiers
        ("![V_X] : p_A(V_X, sk.1)", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Variable(X), Const(skolem_1)))"),
        ("![V_X] : p_A(sk.1(V_X))", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Function(skolem_1, Variable(X))))"),
        ("? [V_X] : (p_A(V_X) & p_B(sk.2))", "LogicQuantifier(EXISTS, Variable(X), LogicConnective(AND, Predicate(A, Variable(X)), Predicate(B, Const(skolem_2))))"),

        # Complex formulas with Skolem
        ("![V_X] : (p_A(V_X) => ? [V_Y] : (p_B(V_Y) & p_C(sk.1(V_X, V_Y))))",
         "LogicQuantifier(FORALL, Variable(X), LogicConnective(IMP, Predicate(A, Variable(X)), LogicQuantifier(EXISTS, Variable(Y), LogicConnective(AND, Predicate(B, Variable(Y)), Predicate(C, Function(skolem_1, Variable(X), Variable(Y)))))))"),

        # Nested Skolem functions
        ("p_A(sk.1(sk.2(V_X)))", "Predicate(A, Function(skolem_1, Function(skolem_2, Variable(X))))"),
        ("p_A(f_B(sk.1(V_X)))", "Predicate(A, Function(B, Function(skolem_1, Variable(X))))"),
    ]

    def test_tptp_formulas(self):
        """Test that original TPTP formulas still parse correctly."""
        parser = CtxProofTPTPParser()
        for expression, result in self.tptp_tests:
            with self.subTest(expression=expression):
                self.assertEqual(repr(parser(expression)), result)

    def test_special_predicate_formulas(self):
        """Test parsing of formulas with $true and $false predicates."""
        parser = CtxProofTPTPParser()
        for expression, result in self.special_predicate_tests:
            with self.subTest(expression=expression):
                self.assertEqual(repr(parser(expression)), result)

    def test_skolem_formulas(self):
        """Test parsing of formulas with Skolem symbols."""
        parser = CtxProofTPTPParser()
        for expression, result in self.skolem_tests:
            with self.subTest(expression=expression):
                self.assertEqual(repr(parser(expression)), result)


if __name__ == "__main__":
    unittest.main()