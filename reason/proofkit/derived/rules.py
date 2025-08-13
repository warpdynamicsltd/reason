from reason.core.fof_ops import Not
from reason.core.fof_types import LogicConnective, FirstOrderFormula
from reason.parser.tree import const
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import *
import reason.proofkit.derived.tautologies as tau


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

def r_imp_imp_iff(p: Ref, q: Ref):
    """
    a -> b, b -> a |- a <-> b
    """
    match formula(p), formula(q):
        case LogicConnective(name=const.IMP, args=[a, b]), LogicConnective(name=const.IMP, args=[b1, a1]) if a == a1 and b == b1:
            r1 = r_and(p, q) # a -> b and b -> a
            r2 = tau.iff_tau(a, b)
            return MOD(r2, r1)
        case _:
            raise RuntimeError("non imp imp iff")

def r_imp_imp_imp(p: Ref, q: Ref):
    """
    a -> b, b -> c |- a -> c
    """
    match formula(p), formula(q):
        case LogicConnective(name=const.IMP, args=[a, b]), \
             LogicConnective(name=const.IMP, args=[b1, c]) if b == b1:
            r1 = r_and(p, q)  # a -> b and b -> c
            r2 = tau.imp_trans(a, b, c)
            return MOD(r2, r1)
        case _:
            raise RuntimeError("non imp imp iff")

def r_iff_revolve(p: Ref):
    """
    a <-> b |- b <-> a
    """
    match formula(p):
        case LogicConnective(name=const.IFF, args=[a, b]):
            r1 = IFO(a, b)
            r2 = MOD(r1, p) # a -> b and b -> a
            r3 = r_and_left(r2) # a -> b
            r4 = r_and_right(r2) # b -> a
            r5 = r_and(r4, r3) # b -> a and a -> b
            r6 = tau.iff_tau(b, a)
            return MOD(r6, r5)
        case _:
            raise RuntimeError("non iff")


def r_iff_imp(p: Ref):
    """
    a <-> b |- a -> b
    """
    match formula(p):
        case LogicConnective(name=const.IFF, args=[a, b]):
            r1 = IFO(a, b)  # a <-> b -> (a -> b) and (c -> b)
            r2 = MOD(r1, p)  # (a -> b) and (b -> a)
            return r_and_left(r2)  # a -> b
        case _:
            raise RuntimeError("non equivalence")

def r_iff_imp_not(p: Ref):
    """
    a <-> b |- ~a -> ~b
    """
    match formula(p):
        case LogicConnective(name=const.IFF, args=[a, b]):
            r1 = IFO(a, b)  # a <-> b -> (a -> b) and (b -> a)
            r2 = MOD(r1, p)  # (a -> b) and (c -> b)
            r3 = r_and_right(r2)  # b -> a
            r4 = tau.imp_inv(a, b)  # (b -> a) -> (~a -> ~b)
            return  MOD(r4, r3)  # ~a -> ~b
        case _:
            raise RuntimeError("non equivalence")

def r_iff_mod(p: Ref, q: Ref):
    """
    a <-> c, a |- c
    """
    r1 = r_iff_imp(p) # a -> c
    return MOD(r1, q)

def r_iff_mod_not(p: Ref, q: Ref):
    """
    a <-> c, ~a |- ~c
    """
    r1 = r_iff_imp_not(p) # ~a -> ~c
    return MOD(r1, q)

def r_iff_or_left(p: Ref, q: Ref):
    """
    a <-> c, a or b |- c or b
    """
    match formula(p), formula(q):
        case (LogicConnective(name=const.IFF, args=[a, c]), LogicConnective(name=const.OR, args=[a1, b])) if a1 == a:
            with Context():
                r3 = ASM(a)
                r4 = r_iff_imp(p) # a -> c
                r5 = MOD(r4, r3) # c
                r6 = ORL(c, b) # c -> c or b
                MOD(r6, r5) # c or b
                r7 = ref() # a -> c or b

            r8 = ORR(c, b) # b -> c or b
            r9 = r_join_cases(r7, r8) # a or b -> c or b
            return MOD(r9, q) # c or b

        case _:
            raise RuntimeError("non equivalence")

def r_iff_or_right(p: Ref, q: Ref):
    """
    a <-> c, b or a |- b or c
    """
    match formula(p), formula(q):
        case (LogicConnective(name=const.IFF, args=[a, c]),
              LogicConnective(name=const.OR, args=[b, a1])) if a1 == a:
            with Context():
                r3 = ASM(a)
                r4 = r_iff_imp(p)  # a -> c
                r5 = MOD(r4, r3)  # c
                r6 = ORR(b, c)  # c -> b or c
                MOD(r6, r5)  # c or b
                r7 = ref()  # a -> b or c

            r8 = ORL(b, c)  # b -> b or c
            r9 = r_join_cases(r8, r7)  # b or a -> b or c
            return MOD(r9, q)  # b or c

        case _:
            raise RuntimeError("not equivalence")
