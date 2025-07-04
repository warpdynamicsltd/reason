import ast
import re

from lark import Transformer, v_args, Token

from reason.parser.utils import v_args_return_with_meta, v_args_with_meta_return_with_meta
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

    @v_args_return_with_meta
    def definition_expression(self, logic_simple):
        return AbstractSyntaxTree(DEFINITION, self._logic_simple(logic_simple))

    @v_args_return_with_meta
    def pick_const_declaration_with_constrain_expression(self, consts, logic_simple):
        return AbstractSyntaxTree(CONST_DECLARATION_WITH_CONSTRAIN, self._logic_simple(logic_simple), *consts)

    @v_args_return_with_meta
    def use_const_declaration_with_constrain_expression(self, consts, logic_simple):
        return AbstractSyntaxTree(CONST_USE_DECLARATION_WITH_CONSTRAIN, self._logic_simple(logic_simple), *consts)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def assumption_expression(self, logic_simple):
        return AbstractSyntaxTree(ASSUMPTION, self._logic_simple(logic_simple))

    @v_args_return_with_meta
    def axiom_expression(self, logic_simple):
        return AbstractSyntaxTree(ATOMIC_AXIOM, self._logic_simple(logic_simple))

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
    def take_const_declaration(self, consts):
        return AbstractSyntaxTree(CONST_DECLARATION, *consts)

    @v_args_return_with_meta
    def use_const_declaration(self, consts):
        return AbstractSyntaxTree(CONST_USE_DECLARATION, *consts)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def context_block(self, expression_list):
        return AbstractSyntaxTree(CONTEXT_BLOCK, *expression_list)

    @v_args_with_meta_return_with_meta
    def theorem_context_block(self, meta, theorem, expression_list):
        return AbstractSyntaxTree(
            THEOREM_CONTEXT_BLOCK,
            self.context_block(meta, [expression_list]),
            self._logic_simple(theorem))

    # @v_args(inline=True)
    @v_args_return_with_meta
    def fname(self, symbol):
        return symbol

    # @v_args(inline=True)
    @v_args_return_with_meta
    def symbol(self, symbol):
        return symbol.value
