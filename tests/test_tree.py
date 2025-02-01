import unittest

from reason.parser import Parser
from reason.parser.tree import GrammarTree

class TestTree(unittest.TestCase):
  def test_flat_to_tree(self):
    parser = Parser()
    gt = GrammarTree('CONJUNCTION', GrammarTree("p"), GrammarTree("q"), GrammarTree("r"), GrammarTree("s"))
  
    self.assertEqual(repr(gt.flat_to_tree('AND')), "AND(AND(AND(p, q), r), s)")
    self.assertEqual(repr(gt.flat_to_tree('AND', left_join=False)), "AND(p, AND(q, AND(r, s)))")

    gt = GrammarTree('CONJUNCTION', GrammarTree("p"))
    self.assertEqual(repr(gt.flat_to_tree('AND', left_join=False)), "p")