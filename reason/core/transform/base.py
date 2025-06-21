from collections import deque
from typing import List

from reason.core import AbstractTerm
from reason.core.fof_types import FirstOrderFormula, LogicConnective, LogicQuantifier, Predicate, Term, Variable
from reason.parser.tree.consts import *


class UniqueVariables:
    def __init__(self, formula, variable_prefix="x"):
        self.variable_index = 1
        self.variable_prefix = variable_prefix

        self.result = self._transform(formula)

    def _transform(self, formula):
        match formula:
            case LogicQuantifier(name=op, args=[var, arg]):
                _var = Variable(f"{self.variable_prefix}{self.variable_index}")
                self.variable_index += 1
                return LogicQuantifier(op, _var, self._transform(arg.replace(var, _var)))

            case AbstractTerm(name=name, args=args):
                return type(formula)(name, *map(self._transform, args))

        return formula


def make_bound_variables_unique(formula: FirstOrderFormula, variable_prefix="x") -> FirstOrderFormula:
    return UniqueVariables(formula, variable_prefix=variable_prefix).result


def expand_iff(formula: FirstOrderFormula):
    match formula:
        case LogicConnective(name=const.IFF, args=[a, b]):
            return LogicConnective(
                AND,
                LogicConnective(IMP, expand_iff(a), expand_iff(b)),
                LogicConnective(IMP, expand_iff(b), expand_iff(a)),
            )

        case AbstractTerm(name=name, args=args):
            return type(formula)(name, *map(expand_iff, args))

        case Predicate(name=name, args=args):
            return formula

    return formula


def quantifier_signature(formula: FirstOrderFormula) -> tuple[FirstOrderFormula, deque[tuple[str, Variable]]]:
    match formula:
        case LogicQuantifier(name=op, args=[var, arg]):
            f, sign = quantifier_signature(arg)
            sign.appendleft((op, var))
            return f, sign

    return formula, deque()


def remove_universal_quantifiers(formula: FirstOrderFormula) -> FirstOrderFormula:
    match formula:
        case LogicQuantifier(name=const.FORALL, args=[var, arg]):
            return remove_universal_quantifiers(arg)

    return formula


def prepend_quantifier_signature(formula: FirstOrderFormula, sign: List[tuple[str, Variable]]) -> FirstOrderFormula:
    if not sign:
        return formula

    return LogicQuantifier(sign[0][0], sign[0][1], prepend_quantifier_signature(formula, sign[1:]))


def invert_quantifier_signature(sign: List[tuple[str, Variable]]) -> List[tuple[str, Variable]]:
    result = []
    for s, var in sign:
        result.append((FORALL if s == EXISTS else EXISTS, var))

    return result


def free_variables(f: Term | FirstOrderFormula) -> set[Variable]:
    match f:
        case Variable(name=name):
            return {Variable(name)}

        case LogicQuantifier(name=op, args=[var, arg]):
            variables = free_variables(arg)
            variables.remove(var)
            return variables

        case AbstractTerm(name=name, args=args):
            res = set()
            for arg in args:
                res.update(free_variables(arg))
            return res

    return set()


def closure(formula):
    variables = free_variables(formula)
    return prepend_quantifier_signature(formula, [(FORALL, var) for var in variables])


def conjunction(*formulas: list[FirstOrderFormula]):
    if len(formulas) == 1:
        return formulas[0]

    res = formulas[0]
    for f in formulas[1:]:
        res = LogicConnective(AND, res, f)

    return res
