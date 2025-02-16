from collections import deque
from typing import List

from reason.core import AbstractTerm
from reason.core.fof import LogicQuantifier, Variable, LogicConnective, Predicate, FirstOrderFormula, Term


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


def expand_iff(formula: FirstOrderFormula):
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
    return prepend_quantifier_signature(formula, [('FORALL', var) for var in variables])

