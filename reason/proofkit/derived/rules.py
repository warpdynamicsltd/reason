from reason.core.fof_ops import Not
from reason.core.fof_types import LogicConnective, FirstOrderFormula
from reason.parser.tree import const
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import formula, ANL, MOD, ANR, AND, DIS, LEM, CON


def r_and_left(p: Ref):
    """
    p and q |- p
    """
    match formula(p):
        case LogicConnective(name=const.AND, args=[a, b]):
            r = ANL(a, b)
            return MOD(r, p)
        case _:
            raise RuntimeError("non and formula")


def r_and_right(p: Ref):
    """
    p and q |- q
    """
    match formula(p):
        case LogicConnective(name=const.AND, args=[a, b]):
            r = ANR(a, b)
            return MOD(r, p)
        case _:
            raise RuntimeError("non and formula")


def r_and(a: Ref, b: Ref):
    """
    p, q |- p and q
    """
    r1 = AND(formula(a), formula(b)) # a -> (b -> (a and b))
    r2 = MOD(r1, a) # (b -> (a and b))
    return MOD(r2, b) # a and b


def r_join_cases(case1: Ref, case2: Ref):
    """
    a -> c, b -> c |- (a or b) -> c
    """
    f1 = formula(case1)
    f2 = formula(case2)
    match f1, f2:
        case LogicConnective(name=const.IMP, args=[a, c]), LogicConnective(name=const.IMP, args=[b, c1]) if c == c1:
            r1 = DIS(a, b, c)
            r2 = MOD(r1, case1)
            return MOD(r2, case2)

        case _:
            raise RuntimeError("non join cases")


def r_join_exclusive_cases(case1: Ref, case2: Ref):
    """
    p -> c, ~p -> c |- c
    """
    f1 = formula(case1)
    f2 = formula(case2)
    match f1, f2:
        case LogicConnective(name=const.IMP, args=[a, c]), LogicConnective(name=const.IMP, args=[b, c1]) if c == c1 and b == Not(a):
            r1 = DIS(a, b, c) # (p -> c) -> ((~p -> c) -> (p or ~p -> c))
            r2 = MOD(r1, case1) # (~p -> c) -> (p or ~p -> c)
            r3 = MOD(r2, case2) # p or ~p -> c
            r4 = LEM(a) # p or ~p
            return MOD(r3, r4) #c

        case _:
            raise RuntimeError("non join cases")


def r_contradiction(a: Ref, b: Ref, outcome: FirstOrderFormula):
    """
    a = p
    b = ~p
    p, ~p |- outcome
    """
    p = formula(a)
    q = formula(b)
    if q == Not(p):
        r1 = CON(p, outcome) # ~p -> (p -> outcome)
        r2 = MOD(r1, b) # (p -> outcome)
        return MOD(r2, a)
    else:
        raise RuntimeError("non contradiction")
