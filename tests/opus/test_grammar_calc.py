import pytest
import unittest

from reason.opus.grammar import GrammarNode, digit, st, end

class TestGrammarAddMul(unittest.TestCase):
    pass_list = [
        "1",
        "12",
        "123+45",
        "123*45",
        "123+45*56",
        "123*45+56",
        "1+2*3+4",
        "(1+2)*3",
        "1*(2+3)",
        "(1+2)*(3+4)",
        "((1+2)*3)+4",
        "1+2+3*4+5",
        "1+2*3*4+5*6",
        "(123)",
        "(12+34)",
        "(12*34)",
        "12+(34*56)",
        "12*(34+56)",
        "(12+34)*56",
        "((12+34)*56)",
        "12+34+56*7",
        "1+2+3*4*5+6+7*8",
        "((1+2)*((3+4)*5))",
        "42+(7*8)+9",
        "999+(1*1)",
        "(999*1)+1",
        "12345+(678*90)",
        "12+(34*56)+78*90",
        "((12+34)*56)+78",
        "(12+(34*56))+78",
        "((12+34)+(56*78))",
        "1+2*3+4*5*6+7",
        "(1+2+3)+(4+5+6)",
        "(1+2)*((3*4)+5)",
        "1+(2*3)+(4+5*6)",
        "1234567890+(9876543210*5)",
    ]

    fail_list = [
        "a",
        "12a",
        "12+",
        "+12",
        "12*",
        "*12",
        "12+56+",
        "12+56+45+",
        "+12+56+45",
        "12+56*(45+)",
        "12*56+45*",
        "(123",
        ")123",
        "123)",
        "(1+2",
        "1+2)",
        "123+)45+56(",
        ")+(",
        "++",
        "1++2",
        "1**2",
        "1*/2",
        "1*(2+)",
        "1+2*",
        "1+2 +",
        "1 + 2",
        "1* 2",
        " 1+2",
        "",
        "123+*456",
        "(+123)+45",
        "(1+2)+*3",
        "123+((45*56)",
        "123+((45+56)",
        "1+(2+3)*",
        "(*1)+2",
        "123+(45+)",
        "(+1*2)",
        "1+2*)3(",
        "1+(2*)3",
    ]

    def test_simple_add_mul(self):
        d = digit()
        e = end()

        number = GrammarNode()
        factor = GrammarNode()
        term = GrammarNode()
        expr = GrammarNode()
        start = GrammarNode()

        number == d | d + number
        factor == number | st("(") + expr + st(")")
        term == factor | factor + st("*") + term
        expr == term | term + st("+") + expr
        start == expr + e

        for s in TestGrammarAddMul.pass_list:
            self.assertEqual(list(start(s))[0][0], len(s))

        for s in TestGrammarAddMul.fail_list:
            self.assertEqual(list(start(s)), [])