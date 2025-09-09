import unittest
from reason.opus.grammar import GrammarNode, digit, st, end

class TestLongAssignmentGrammar(unittest.TestCase):
    pass_list = [
        "a=1;",
        "x1=12;y=3;",
        "var=1+2*3;",
        "aaa=1+2*3+4*5;y=aaa*2+2;",
        "a=1;b=2;c=3;d=4;",
        "x=1+2;y=x*3+4;z=y+1+2+3+4*5;",
        "a=1;b=2;c=a+b*3;d=c*4+5;e=d+6*7+8*9+10;",
        "v=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15;",
        "x=1+2*3+4*5+6*7+8*9+10*11;y=x+1+2*3+4+5*6;",
        "var=42;va=var+100;vb=va*2+3;vc=vb+4;vd=vc+5*6+7*8+9*10;",
        "long_var=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20;",
        "long_var=long_var1*2+long_var2*3+long_var3*4+long4_var*5+long_var*6;",
        ";".join(f"x{i}={i}+(x{i-1}+{i})" for i in range(2, 100)) + ";",
    ]

    fail_list = [
        "a=",
        "=1;",
        "a1+2;",
        "a=1+;",
        "a=1*;",
        "a=;b=2;",
        "a1==2;",
        "a=1+2;b=;",
        "a=1+2;;",
        "1a=1;",
        "a 1=1;",
        "a==2;",
        "=a+1;",
        "a=1+2+;",
        "a=1+2*;",
        "a=1x2;",
        "a=b*;",
        "a=;",
        "x==2;",
        ";a=2;",
        "a=1+2; b=3",  # whitespace not supported like this
    ]

    def test_long_assignments(self):
        dig = digit()
        letter = GrammarNode()
        alpha = GrammarNode()
        ident = GrammarNode()
        number = GrammarNode()
        expr = GrammarNode()
        term = GrammarNode()
        factor = GrammarNode()
        post_fix = GrammarNode()
        assignment = GrammarNode()
        seq = GrammarNode()
        e = end()

        # Grammar for identifiers: a letter followed by letters or digits
        letter == st("a") | st("b") | st("c") | st("d") | st("e") | st("f") | st("g") \
                    | st("h") | st("i") | st("j") | st("k") | st("l") | st("m") | st("n") \
                    | st("o") | st("p") | st("q") | st("r") | st("s") | st("t") | st("u") \
                    | st("v") | st("w") | st("x") | st("y") | st("z") | st("_")

        alpha = letter | dig

        post_fix == alpha | alpha + post_fix
        ident == letter | letter + post_fix

        number == dig | dig + number
        factor == number | ident | st("(") + expr + st(")")
        term == factor | factor + st("*") + term
        expr == term | term + st("+") + expr
        assignment == ident + st("=") + expr + st(";")
        seq == assignment | assignment + seq
        start = seq + e

        for s in TestLongAssignmentGrammar.pass_list:
            self.assertEqual(list(start(s))[0][0], len(s), msg=s)

        for s in TestLongAssignmentGrammar.fail_list:
            self.assertEqual(list(start(s)), [], msg=s)
