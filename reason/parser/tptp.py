from lark import Transformer, v_args, Token
from reason.parser.tree import *
from reason.core.fof import *

class TPTPTreeToAbstractSyntaxTree(Transformer):
    variables_list = list
    term_list = list

    @v_args(inline=True)
    def variable(self, arg):
        return Variable(arg.value)

    @v_args(inline=True)
    def const(self, arg):
        return Const(arg.value)

    @v_args(inline=True)
    def fname(self, arg):
        return arg.value

    @v_args(inline=True)
    def predicate_name(self, arg):
        return Predicate(arg)

    @v_args(inline=True)
    def composed_term(self, fname, args):
        return Function(fname, *args)

    @v_args(inline=True)
    def composed_predicate(self, fname, args):
        return Predicate(fname, *args)

    @v_args(inline=True)
    def bracket(self, arg):
        return arg

    @v_args(inline=True)
    def logic_neg_op(self, arg):
        return LogicConnective(NEG, arg)

    @v_args(inline=True)
    def logic_and_op(self, pred1, pred2):
        return LogicConnective(AND, pred1, pred2)

    @v_args(inline=True)
    def logic_or_op(self, pred1, pred2):
        return LogicConnective(OR, pred1, pred2)

    @v_args(inline=True)
    def term(self, term):
        return term

    @v_args(inline=True)
    def predicate(self, predicate):
        return predicate

    @v_args(inline=True)
    def formula(self, formula):
        return formula

