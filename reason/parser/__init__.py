from reason.parser.lark import get_lark_parser
from importlib.resources import files
from reason.parser.tree import OperatorGrammarCreator, ReasonTreeToAbstractSyntaxTree, AbstractSyntaxTree
from reason.parser.tree.program import ProgramTreeToAbstractSyntaxTree


class Parser:
    def __init__(self):
        self.ogc = OperatorGrammarCreator("abstract_term", "logic_simple", "logic_level")
        with open(str(files("reason") / "assets" / "lark" / "reason.lark")) as f:
            self.dynamic_code = self.ogc.create_lark_code()
            code = f.read() + self.dynamic_code
            self.save_code(code)
            self.reason_parser = get_lark_parser(code, start="logic_simple", lexer="basic")

    def save_code(self, code):
        with open(str(files("reason") / "assets" / "lark" / "reason_gen.lark"), "w") as f:
            f.write(code)

    def __call__(self, text: str) -> AbstractSyntaxTree:
        tree = self.reason_parser.parse(text)
        return ReasonTreeToAbstractSyntaxTree(level_prefix=self.ogc.prefix).transform(tree)


class ProgramParser:
    def __init__(self):
        self.ogc = OperatorGrammarCreator("abstract_term", "logic_simple", "logic_level")
        with open(str(files("reason") / "assets" / "lark" / "reason.lark")) as f:
            self.dynamic_code = self.ogc.create_lark_code()
            code = f.read() + self.dynamic_code
            self.reason_parser = get_lark_parser(code, start="expression_list", lexer="basic")

    def __call__(self, text: str) -> list[AbstractSyntaxTree]:
        tree = self.reason_parser.parse(text)
        return ProgramTreeToAbstractSyntaxTree(level_prefix=self.ogc.prefix).transform(tree)
