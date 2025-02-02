from lark import Transformer, Lark
from reason.core import AbstractTerm
from importlib.resources import files
from reason.parser.tree import OperatorGrammarCreator, TreeToGrammarTree


class Parser:
  def __init__(self):
    self.ogc = OperatorGrammarCreator("abstract_term", "logic_simple", "logic_level")
    with open(files('reason') / "assets" / "lark" / "reason.lark") as f:
      code = f.read() + self.ogc.create_lark_code()
      self.reason_parser = Lark(code, start='logic_simple', lexer='basic')

  def __call__(self, text):
    tree = self.reason_parser.parse(text)
    return TreeToGrammarTree(level_prefix=self.ogc.prefix).transform(tree)
