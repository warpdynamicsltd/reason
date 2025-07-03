from reason.parser.tree import AbstractSyntaxTree
from reason.parser.tree.consts import *

class SelectionAxiomsBuilder:
    def __init__(self, ast: AbstractSyntaxTree):
        self.ast = ast
        self.axioms = []

    def _transform(self, ast: AbstractSyntaxTree):

        match ast:
            case AbstractSyntaxTree(name=const.SELECT, args=[index_tree, selector_tree]):


        return AbstractSyntaxTree(ast.name, *map(self._transform, ast.args))