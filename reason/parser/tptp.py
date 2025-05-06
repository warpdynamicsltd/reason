from lark import Transformer, Lark
from importlib.resources import files
from reason.core.fof_types import Const, FirstOrderFormula, Function, LogicConnective, Predicate, Variable
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
        value = arg.value
        if value[:2] == "c_":
            value = value[2:]
        return Const(value)

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


class TPTPParser:
    def __init__(self):
        with open(str(files("reason") / "assets" / "lark" / "tptp.lark")) as f:
            code = f.read()
            self.tptp_parser = Lark(code, start="formula", lexer="basic")

    def __call__(self, text: str) -> FirstOrderFormula:
        tree = self.tptp_parser.parse(text)
        return TPTPTreeToAbstractSyntaxTree().transform(tree)
