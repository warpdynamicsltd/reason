import unittest

from reason.parser import Parser


class TestParser(unittest.TestCase):
    tests = [
        ("P or Q or R or T", "OR(OR(OR(P, Q), R), T)"),
        ("P or Q or R and T", "OR(OR(P, Q), AND(R, T))"),
        ("P or Q → R and T", "IMP(OR(P, Q), AND(R, T))"),
        ("Any(x, (P(x) → Q) and P → Q)", "Any(x, IMP(AND(IMP(P(x), Q), P), Q))"),
        ("Any(x, (P(x) → Q) and (P → Q))", "Any(x, AND(IMP(P(x), Q), IMP(P, Q)))"),
        ("Any(x, P(x) → Q and P → Q)", "Any(x, IMP(IMP(P(x), AND(Q, P)), Q))"),
        (
            "Exists(y, P(y) or Q(y) or R(y) and E(y)) → Any(x, P(x) → Q and P → Q)",
            "IMP(Exists(y, OR(OR(P(y), Q(y)), AND(R(y), E(y)))), Any(x, IMP(IMP(P(x), AND(Q, P)), Q)))",
        ),
        (
            "Exists(y, P(y) or Q(y) or R(y) and Any(z, ~P(z) → R(y) and Q(y))) → Any(x, P(x) → Q and P → Q)",
            "IMP(Exists(y, OR(OR(P(y), Q(y)), AND(R(y), Any(z, IMP(NEG(P(z)), AND(R(y), Q(y))))))), Any(x, IMP(IMP(P(x), AND(Q, P)), Q)))",
        ),
        (
            "Exists(y, ~P(y) or Q(y) or R(y) and ~Any(z, ~P(z) → R(y) and Q(y))) → Any(x, P(x) → Q and P → Q)",
            "IMP(Exists(y, OR(OR(NEG(P(y)), Q(y)), AND(R(y), NEG(Any(z, IMP(NEG(P(z)), AND(R(y), Q(y)))))))), Any(x, IMP(IMP(P(x), AND(Q, P)), Q)))",
        ),
        (
            "Exists(y, ~P(y) or Q(y) or R(y) and ~Any(z, ~(P(z) → R(y)) and Q(y))) → Any(x, P(x) → Q and P → Q)",
            "IMP(Exists(y, OR(OR(NEG(P(y)), Q(y)), AND(R(y), NEG(Any(z, AND(NEG(IMP(P(z), R(y))), Q(y))))))), Any(x, IMP(IMP(P(x), AND(Q, P)), Q)))",
        ),
        ("~P and ~Q → ~(P or Q)", "IMP(AND(NEG(P), NEG(Q)), NEG(OR(P, Q)))"),
    ]

    def test_formulas(self):
        parser = Parser()
        for expression, result in self.tests:
            self.assertEqual(repr(parser(expression)), result)
