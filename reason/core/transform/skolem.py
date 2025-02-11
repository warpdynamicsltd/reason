from collections import deque
from typing import List

from reason.core.fof import *


def expand_iff(formula):
    match formula:
        case LogicConnective(name="IFF", args=[a, b]):
            return LogicConnective(
                "AND",
                LogicConnective("IMP", expand_iff(a), expand_iff(b)),
                LogicConnective("IMP", expand_iff(b), expand_iff(a)),
            )

        case AbstractTerm(name=name, args=args):
            return type(formula)(name, *map(expand_iff, args))

        case Predicate(name=name, args=args):
            return formula

    return formula


class UniqueVariables:
    def __init__(self):
        self.variable_index = 1

    def __call__(self, formula):
        match formula:
            case LogicQuantifier(name=op, args=[var, arg]):
                _var = Variable(f"x{self.variable_index}")
                self.variable_index += 1
                return LogicQuantifier(op, _var, self(arg.replace(var, _var)))

            case AbstractTerm(name=name, args=args):
                return type(formula)(name, *map(self.__call__, args))

        return formula


def quantifier_signature(formula: FirstOrderFormula) -> tuple[FirstOrderFormula, deque[tuple[str, Variable]]]:
    match formula:
        case LogicQuantifier(name=op, args=[var, arg]):
            f, sign = quantifier_signature(arg)
            sign.appendleft((op, var))
            return f, sign

    return formula, deque()


def prepend_quantifier_signature(formula: FirstOrderFormula, sign: List[tuple[str, Variable]]) -> FirstOrderFormula:
    if not sign:
        return formula

    return LogicQuantifier(sign[0][0], sign[0][1], prepend_quantifier_signature(formula, sign[1:]))


def invert_quantifier_signature(sign: List[tuple[str, Variable]]) -> List[tuple[str, Variable]]:
    result = []
    for s, var in sign:
        result.append(("FORALL" if s == "EXISTS" else "EXISTS", var))

    return result


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


def prenex_normal(formula: FirstOrderFormula) -> FirstOrderFormula:
    formula = expand_iff(formula)
    formula = UniqueVariables()(formula)
    return prenex_normal_raw(formula)


# def skolem(formula):
#     match formula:
