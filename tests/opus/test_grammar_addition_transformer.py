import pytest
import unittest

from reason.parser import AbstractSyntaxTree
from reason.opus.transformer import Transformer
from reason.opus.grammar import GrammarNode, digit, st, end, repeat

class AddingTransformer(Transformer):
    def number(self, digits):
        return int("".join(digits))

    def bracket(self, value):
        lb, value, rb = value
        return value

    def repeat_direct_sum(self, args):
        if args:
            ast = AbstractSyntaxTree("ADD", *[n for n, op in args])
            return ast.flat_to_tree("ADD")

    def sum(self, arg):
        s, n = arg
        if s:
            return AbstractSyntaxTree("ADD", s, n)
        else:
            return n

    def start(self, value):
        (value, e) = value
        return value


class TestGrammarAdditionTransformer(unittest.TestCase):
    pass_list = [
        ("1", 1),
        ("12", 12),
        ("1+2", AbstractSyntaxTree("ADD", 1, 2)),
        ("1+2+3", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 1, 2), 3)),
        ("1+2+3+4", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 1, 2), 3), 4)),
        ("1+2+3+4+5", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 1, 2), 3), 4), 5)),
        ("23+145+45", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 23, 145), 45)),
        ("(1)", 1),
        ("(1+2)", AbstractSyntaxTree("ADD", 1, 2)),
        ("(1+2+3)", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 1, 2), 3)),
        ("(12+34)+16", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 12, 34), 16)),
        ("12+(34+16)", AbstractSyntaxTree("ADD", 12, AbstractSyntaxTree("ADD", 34, 16))),
        ("((1))", 1),
        ("((1+2))", AbstractSyntaxTree("ADD", 1, 2)),
        ("(1)+(2+3)", AbstractSyntaxTree("ADD", 1, AbstractSyntaxTree("ADD", 2, 3))),
        ("(7)+(8)+(9)", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 7, 8), 9)),
        ("(2+3)+(4+5)", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 2, 3), AbstractSyntaxTree("ADD", 4, 5))),
        ("(100+20+3)+5",
         AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 100, 20), 3), 5)),
        ("15+(25+(35+45))",
         AbstractSyntaxTree("ADD", 15, AbstractSyntaxTree("ADD", 25, AbstractSyntaxTree("ADD", 35, 45)))),
        ("1+23+(456+7+8)", AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 1, 23),
                                              AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 456, 7), 8))),
        ("12345", 12345),
        ("((12+34)+(56+78))+90", AbstractSyntaxTree("ADD",
                                                    AbstractSyntaxTree("ADD", AbstractSyntaxTree("ADD", 12, 34),
                                                                       AbstractSyntaxTree("ADD", 56, 78)), 90)),
    ]

    def test_simple_addition(self):
        d = digit()
        e = end()

        number = GrammarNode("number")
        start = GrammarNode("start")
        sum = GrammarNode("sum")
        exp = GrammarNode("exp")

        number == repeat(d)
        exp == number | st("(") + sum + st(")") >> "bracket"
        sum == repeat(exp + st("+") >> "direct_sum") + exp
        start == sum + e

        for s, t in TestGrammarAdditionTransformer.pass_list:
            [(i, node)] = start(s)
            self.assertEqual(AddingTransformer().transform(node), t, msg=s)