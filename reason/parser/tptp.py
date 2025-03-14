from lark import Transformer, v_args, Token
from reason.parser.tree import *
from reason.core.fof import *
from reason.core.transform.base import prepend_quantifier_signature


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
        if fname[:2] == "f_":
            fname = fname[2:]
        return Function(fname, *args)

    @v_args(inline=True)
    def composed_predicate(self, fname, args):
        if fname[:2] == "p_":
            fname = fname[2:]
        return Predicate(fname, *args)

    @v_args(inline=True)
    def terms_equality(self, term1, term2):
        return Predicate("EQ", term1, term2)

    @v_args(inline=True)
    def terms_inequality(self, term1, term2):
        return LogicConnective("NEG", Predicate("EQ", term1, term2))

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
    def logic_imp_op(self, pred1, pred2):
        return LogicConnective(IMP, pred1, pred2)

    @v_args(inline=True)
    def logic_iff_op(self, pred1, pred2):
        return LogicConnective(IFF, pred1, pred2)

    @v_args(inline=True)
    def exists_quantifier(self, variables_list, formula):
        return prepend_quantifier_signature(formula, [(EXISTS, v) for v in variables_list])

    @v_args(inline=True)
    def forall_quantifier(self, variables_list, formula):
        return prepend_quantifier_signature(formula, [(FORALL, v) for v in variables_list])

    @v_args(inline=True)
    def term(self, term):
        return term

    @v_args(inline=True)
    def predicate(self, predicate):
        return predicate

    @v_args(inline=True)
    def formula(self, formula):
        return formula
