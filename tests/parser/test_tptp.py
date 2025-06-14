import unittest

from reason.parser.tptp import TPTPParser


class TestTPTPParser(unittest.TestCase):
    tests = [
        ("![X] : p_A(X)", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Variable(X)))"),
        ("![X] : p_A(f_inc(X))", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Function(inc, Variable(X))))"),
        ("![X, Y, Z] : p_A(f_inc(X), Z, Y)", "LogicQuantifier(FORALL, Variable(X), LogicQuantifier(FORALL, Variable(Y), LogicQuantifier(FORALL, Variable(Z), Predicate(A, Function(inc, Variable(X)), Variable(Z), Variable(Y)))))"),
        #("![X] : p_A(X, a)", "LogicQuantifier(FORALL, Variable(X), Predicate(A, Variable(X), Const(a)))"),
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

    def test_formulas(self):
        parser = TPTPParser()
        for expression, result in self.tests:
            self.assertEqual(repr(parser(expression)), result)