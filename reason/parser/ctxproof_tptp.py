from lark import Transformer
from importlib.resources import files

from reason.parser.lark import get_lark_parser
from reason.core.fof_ops import *
from reason.core.fof_types import Const, FirstOrderFormula, Function, LogicConnective, Predicate, Variable
from reason.parser.tree import *
from reason.core.fof import *
from reason.core.transform.base import prepend_quantifier_signature
from reason.parser.tree.consts import *
from reason.vampire.translator import name_tptp_decode


class CtxProofTPTPTreeToAbstractSyntaxTree(Transformer):
    variables_list = list
    term_list = list

    @v_args(inline=True)
    def variable(self, arg):
        value = arg.value
        # Strip V_ prefix added by to_tptp_fof
        if value[:2] == "V_":
            value = value[2:]
        return Variable(value)

    @v_args(inline=True)
    def const(self, arg):
        value = arg.value
        if value[:2] == "c_":
            value = value[2:]
        return Const(name_tptp_decode(value))

    @v_args(inline=True)
    def skolem_symbol(self, arg):
        """Handle Skolem symbol as a constant (e.g., sk.1, sk.23.4)"""
        # Convert sk.X.Y back to skolem_X_Y format
        value = arg.value
        if value.startswith("sk."):
            # sk.1.2.3 -> skolem_1_2_3
            rest = value[3:]  # Remove "sk."
            value = "skolem_" + rest.replace(".", "_")
        return Const(value)

    @v_args(inline=True)
    def fname(self, arg):
        return arg.value

    @v_args(inline=True)
    def true_predicate(self):
        """Handle $true predicate"""
        return TruePred()

    @v_args(inline=True)
    def false_predicate(self):
        """Handle $false predicate"""
        return FalsePred()

    @v_args(inline=True)
    def predicate_name(self, arg):
        # Strip p_ prefix added by to_tptp_fof for simple predicates
        value = arg
        if value[:2] == "p_":
            value = value[2:]
        return Predicate(value)

    @v_args(inline=True)
    def composed_term(self, fname, args):
        if fname[:2] == "f_":
            fname = fname[2:]
        return Function(fname, *args)

    @v_args(inline=True)
    def skolem_term(self, skolem, args):
        """Handle Skolem symbol with arguments as a function (e.g., sk.2(X, Y))"""
        return Function(skolem.name, *args)

    @v_args(inline=True)
    def composed_predicate(self, fname, args):
        if fname[:2] == "p_":
            fname = fname[2:]
        return Predicate(fname, *args)

    @v_args(inline=True)
    def skolem_predicate_name(self, skolem):
        """Handle Skolem symbol as a predicate name (e.g., sk.1)"""
        return Predicate(skolem.name)

    @v_args(inline=True)
    def skolem_predicate(self, skolem, args):
        """Handle Skolem symbol as a predicate with arguments (e.g., sk.2(X, Y))"""
        return Predicate(skolem.name, *args)

    @v_args(inline=True)
    def terms_equality(self, term1, term2):
        return Predicate(EQ, term1, term2)

    @v_args(inline=True)
    def terms_inequality(self, term1, term2):
        return LogicConnective(NEG, Predicate(EQ, term1, term2))

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


class CtxProofTPTPParser:
    def __init__(self):
        with open(str(files("reason") / "assets" / "lark" / "ctxproof_tptp.lark")) as f:
            code = f.read()
            self.ctxproof_tptp_parser = get_lark_parser(code, start="formula", lexer="dynamic")

    def __call__(self, text: str) -> FirstOrderFormula:
        tree = self.ctxproof_tptp_parser.parse(text)
        return CtxProofTPTPTreeToAbstractSyntaxTree().transform(tree)