import unittest

from reason.parser import Parser
from reason.parser.tree import AbstractSyntaxTree


class TestTree(unittest.TestCase):
    def test_flat_to_tree(self):
        parser = Parser()
        gt = AbstractSyntaxTree(
            "CONJUNCTION",
            AbstractSyntaxTree("p"),
            AbstractSyntaxTree("q"),
            AbstractSyntaxTree("r"),
            AbstractSyntaxTree("s"),
        )

        self.assertEqual(gt.flat_to_tree("AND").show(), "AND(AND(AND(p, q), r), s)")
        self.assertEqual(gt.flat_to_tree("AND", left_join=False).show(), "AND(p, AND(q, AND(r, s)))")

        gt = AbstractSyntaxTree("CONJUNCTION", AbstractSyntaxTree("p"))
        self.assertEqual(gt.flat_to_tree("AND", left_join=False).show(), "p")
