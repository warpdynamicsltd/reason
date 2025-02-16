from reason.core.fof import *
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    invert_quantifier_signature


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


def skolem(formula):
    formula = prenex_normal(formula)
    formula, signature = quantifier_signature(formula)

    vars = []
    index = 1
    for quantifier, variable in signature:
        if quantifier == 'EXISTS':
            if vars:
                skolem_term = Function(f"s{index}", *vars)
            else:
                skolem_term = Const(f"s{index}")

            formula = formula.replace(variable, skolem_term)
            index += 1
        else:
            vars.append(variable)

    return formula

