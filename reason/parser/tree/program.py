import ast
import re

from lark import Transformer, v_args, Token

from reason.parser.utils import v_args_return_with_meta
from reason.parser.tree import AbstractTerm, ReasonTreeToAbstractSyntaxTree, AbstractSyntaxTree
from reason.parser.tree.consts import *


class ProgramTreeToAbstractSyntaxTree(Transformer):
    fname_list = list
    expression_list = list

    def __init__(self, level_prefix, *args, **kwargs):
        self.level_prefix = level_prefix
        Transformer.__init__(self, *args, **kwargs)

    def _logic_simple(self, logic_simple):
        return ReasonTreeToAbstractSyntaxTree(level_prefix=self.level_prefix).transform(logic_simple)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def logic_expression(self, logic_simple):
        return AbstractSyntaxTree(ASSERTION, self._logic_simple(logic_simple))

    # @v_args(inline=True)
    @v_args_return_with_meta
    def assumption_expression(self, logic_simple):
        return AbstractSyntaxTree(ASSUMPTION, self._logic_simple(logic_simple))

    # @v_args(inline=True)
    @v_args_return_with_meta
    def conclusion_expression(self, logic_simple):
        return AbstractSyntaxTree(CONCLUSION, self._logic_simple(logic_simple))

    # @v_args(inline=True)
    @v_args_return_with_meta
    def include_expression(self, s):
        return AbstractSyntaxTree(INCLUDE_FILE, ast.literal_eval(s.value))

    # @v_args(inline=True)
    @v_args_return_with_meta
    def const_declaration(self, consts):
        return AbstractSyntaxTree(CONST_DECLARATION, *consts)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def context_block(self, expression_list):
        return AbstractSyntaxTree(CONTEXT_BLOCK, *expression_list)

    @v_args_return_with_meta
    def theorem_context_block(self, theorem, expression_list):
        return AbstractSyntaxTree(
            THEOREM_CONTEXT_BLOCK,
            AbstractSyntaxTree(CONTEXT_BLOCK, *expression_list),
            AbstractSyntaxTree(CONCLUSION, self._logic_simple(theorem)))

    # @v_args(inline=True)
    @v_args_return_with_meta
    def fname(self, symbol):
        return symbol

    # @v_args(inline=True)
    @v_args_return_with_meta
    def symbol(self, symbol):
        return symbol.value
