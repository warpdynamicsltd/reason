from reason.core.fof import *
from reason.core.fof_types import Const, FirstOrderFormula, Function, LogicConnective, LogicQuantifier, Predicate
from reason.core.transform.base import (
    make_bound_variables_unique,
    expand_iff,
    quantifier_signature,
    prepend_quantifier_signature,
    invert_quantifier_signature,
)
from reason.core.transform.graph.skolem import SkolemFormulaToGraphLab
from reason.tools.unique_repr import UniqueRepr


def quantifier_signature_to_str_value(signature):
    return "".join(map(lambda pair: pair[0], signature))


def prenex_normal_raw(formula: FirstOrderFormula) -> FirstOrderFormula:
    match formula:
        case LogicConnective(name="NEG", args=[arg]):
            f = prenex_normal_raw(arg)
            f, sign = quantifier_signature(f)
            return prepend_quantifier_signature(LogicConnective("NEG", f), invert_quantifier_signature(list(sign)))

        case LogicConnective(name=op, args=[a, b]) if op in {"AND", "OR"}:
            a = prenex_normal_raw(a)
            b = prenex_normal_raw(b)
            a, sign_a = quantifier_signature(a)
            b, sign_b = quantifier_signature(b)

            return prepend_quantifier_signature(LogicConnective(op, a, b), list(sign_a) + list(sign_b))

        case LogicConnective(name="IMP", args=[a, b]):
            a = prenex_normal_raw(a)
            b = prenex_normal_raw(b)
            a, sign_a = quantifier_signature(a)
            b, sign_b = quantifier_signature(b)

            return prepend_quantifier_signature(
                LogicConnective("IMP", a, b), invert_quantifier_signature(list(sign_a)) + list(sign_b)
            )

        case LogicQuantifier(name=op, args=[var, arg]):
            return LogicQuantifier(op, var, prenex_normal_raw(arg))

        case Predicate(name=op, args=args):
            return formula

    raise RuntimeError(f"unexpected formula: {formula}")


def prenex_normal(formula: FirstOrderFormula, variable_prefix="x") -> FirstOrderFormula:
    formula = expand_iff(formula)
    formula = make_bound_variables_unique(formula, variable_prefix=variable_prefix)
    return prenex_normal_raw(formula)


def skolem(formula, skolem_prefix="s", variable_prefix="x") -> FirstOrderFormula:
    formula = prenex_normal(formula, variable_prefix=variable_prefix)
    formula, signature = quantifier_signature(formula)

    vars = []
    index = 1
    for quantifier, variable in signature:
        if quantifier == "EXISTS":
            if vars:
                skolem_term = Function(f"{skolem_prefix}{index}", *vars)
            else:
                skolem_term = Const(f"{skolem_prefix}{index}")

            formula = formula.replace(variable, skolem_term)
            index += 1
        else:
            vars.append(variable)

    return formula


class SkolemUniqueRepr:
    def __init__(self, formula):
        self.translate = {}
        self.translate_inv = {}
        self.result = self._transform(formula)

    def get_form_id(self, form):
        if form in self.translate:
            return self.translate[form]
        else:
            res = len(self.translate) + 2
            self.translate[form] = res
            self.translate_inv[res] = form
            return res

    def unique(self, formula: FirstOrderFormula) -> UniqueRepr:
        match formula:
            case Predicate():
                return UniqueRepr(self.get_form_id(formula))

            case LogicConnective(name="AND", args=[a, b]):
                return self.unique(a) * self.unique(b)

            case LogicConnective(name="OR", args=[a, b]):
                A = self.unique(a)
                B = self.unique(b)
                return A + B + A * B

            case LogicConnective(name="NEG", args=[a]):
                return UniqueRepr(1) + self.unique(a)

            case LogicConnective(name="IMP", args=[a, b]):
                A = self.unique(a)
                B = self.unique(b)
                return UniqueRepr(1) + A + A * B

            case LogicConnective(name="IFF", args=[a, b]):
                A = self.unique(a)
                B = self.unique(b)
                return UniqueRepr(1) + A + B

        raise RuntimeError(f"unexpected formula: {formula}")

    def _transform(self, formula: FirstOrderFormula):
        res = []
        unique_repr = self.unique(formula)
        for addend in unique_repr.get_sorted():
            item = []
            for factor in addend:
                if factor != 1:
                    item.append(self.translate_inv[factor])
                else:
                    item.append(factor)
            res.append(tuple(item))

        return tuple(res)


def skolem_unique_repr(formula: FirstOrderFormula, skolem_prefix="s", variable_prefix="x"):
    formula = skolem(formula, skolem_prefix=skolem_prefix, variable_prefix=variable_prefix)
    return SkolemUniqueRepr(formula).result


def skolem_sha256(formula: FirstOrderFormula, skolem_prefix="s", variable_prefix="x"):
    return SkolemFormulaToGraphLab(
        skolem_unique_repr(formula, skolem_prefix=skolem_prefix, variable_prefix=variable_prefix)
    ).sha256
