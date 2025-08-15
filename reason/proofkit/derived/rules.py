import inspect

from reason.proofkit.kernel.proof import *
import reason.proofkit.derived.tautologies as tau

class RuleError(Exception):
    pass

def rule(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except RuleError as e:
            raise RuleError(f"schema {inspect.getdoc(f)} not matched")

    return wrapper

@rule
def r_and_left(r1: Ref):
    """
    p and q |- p
    """
    match formula(r1):
        case LogicConnective(name=const.AND, args=[a, b]):
            r2 = ANL(a, b)
            return MOD(r2, r1)

    raise RuleError()


@rule
def r_and_right(r1: Ref):
    """
    p and q |- q
    """
    match formula(r1):
        case LogicConnective(name=const.AND, args=[a, b]):
            r2 = ANR(a, b)
            return MOD(r2, r1)

    raise RuleError()


@rule
def r_and(r1: Ref, r2: Ref):
    """
    p, q |- p and q
    """
    r3 = AND(formula(r1), formula(r2)) # a -> (b -> (a and b))
    r4 = MOD(r3, r1) # (b -> (a and b))
    return MOD(r4, r2) # a and b

@rule
def r_or_left(r1: Ref, f: FirstOrderFormula):
    """
    p |- p or q
    """
    r2 = ORL(formula(r1), f)
    return MOD(r2, r1)

@rule
def r_or_right(f: FirstOrderFormula, r1: Ref):
    """
    q |- p or q
    """
    r2 = ORR(f, formula(r1))
    return MOD(r2, r1)


@rule
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

@rule
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

    raise RuleError()

@rule
def r_contradiction(r1: Ref, r2: Ref, outcome: FirstOrderFormula):
    """
    p, ~p |- outcome
    """
    p = formula(r1)
    not_p = formula(r2)
    if not_p == Not(p):
        r3 = CON(p, outcome) # ~p -> (p -> outcome)
        r4 = MOD(r3, r2) # (p -> outcome)
        return MOD(r4, r1)

    raise RuleError()

@rule
def r_imp_imp_iff(r1: Ref, r2: Ref):
    """
    a -> b, b -> a |- a <-> b
    """
    match formula(r1), formula(r2):
        case LogicConnective(name=const.IMP, args=[a, b]), LogicConnective(name=const.IMP, args=[b1, a1]) if a == a1 and b == b1:
            r3 = IFI(a, b) # (a -> b) -> ( (b -> a) -> (a <-> b) )
            r4 = MOD(r3, r1)
            return MOD(r4, r2)

    raise RuleError()

@rule
def r_imp_trans(r1: Ref, r2: Ref):
    """
    a -> b, b -> c |- a -> c
    """
    match formula(r1), formula(r2):
        case LogicConnective(name=const.IMP, args=[a, b]), \
            LogicConnective(name=const.IMP, args=[b1, c]) if b == b1:
            with Context():
                r3 = ASM(a) # a
                r4 = MOD(r1, r3) # b
                MOD(r2, r4) # c
                return ref()

    return RuleError()

@rule
def r_iff_trans(r1: Ref, r2: Ref):
    """
    a <-> b, b <-> c |- a <-> c
    """
    match formula(r1), formula(r2):
        case LogicConnective(name=const.IFF, args=[a, b]), \
            LogicConnective(name=const.IFF, args=[b1, c]) if b == b1:
            r3 = IFO(a, b)
            r4 = MOD(r3, r1) # a -> b and b -> a
            r5 = IFO(b, c)
            r6 = MOD(r5, r2) # b -> c and c -> b
            r7 = r_and_left(r4) # a -> b
            r8 = r_and_left(r6) # b -> c
            r9 = r_imp_trans(r7, r8) # a -> c
            r10 = r_and_right(r4) # b -> a
            r11 = r_and_right(r6) # c -> b
            r12 = r_imp_trans(r11, r10) # c -> a
            return r_imp_imp_iff(r9, r12)

    raise RuleError()


    return RuleError()

@rule
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

    raise RuleError()

@rule
def r_iff_imp(p: Ref):
    """
    a <-> b |- a -> b
    """
    match formula(p):
        case LogicConnective(name=const.IFF, args=[a, b]):
            r1 = IFO(a, b)  # a <-> b -> (a -> b) and (c -> b)
            r2 = MOD(r1, p)  # (a -> b) and (b -> a)
            return r_and_left(r2)  # a -> b

    raise RuleError()

@rule
def r_iff_imp_not(p: Ref):
    """
    a <-> b |- ~a -> ~b
    """
    match formula(p):
        case LogicConnective(name=const.IFF, args=[a, b]):
            r1 = IFO(a, b)  # a <-> b -> (a -> b) and (b -> a)
            r2 = MOD(r1, p)  # (a -> b) and (b -> a)
            r3 = r_and_right(r2)  # b -> a
            r4 = tau.imp_inv(b, a)  # (b -> a) -> (~a -> ~b)
            return  MOD(r4, r3)  # ~a -> ~b

    raise RuleError()

@rule
def r_iff_mod(r1: Ref, r2: Ref):
    """
    a <-> c, a |- c
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, _]) if a == formula(r2):
            r3 = r_iff_imp(r1) # a -> c
            return MOD(r3, r2)

    raise RuleError()

@rule
def r_iff_mod_not(r1: Ref, r2: Ref):
    """
    a <-> c, ~a |- ~c
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, _]) if Not(a) == formula(r2):
            r3 = r_iff_imp_not(r1) # ~a -> ~c
            return MOD(r3, r2)

    raise RuleError()

@rule
def r_iff_or_left(r1: Ref, r2: Ref):
    """
    a <-> c, a or b |- c or b
    """
    match formula(r1), formula(r2):
        case (LogicConnective(name=const.IFF, args=[a, c]), LogicConnective(name=const.OR, args=[a1, b])) if a1 == a:
            with Context():
                r3 = ASM(a)
                r4 = r_iff_imp(r1) # a -> c
                r5 = MOD(r4, r3) # c
                r6 = ORL(c, b) # c -> c or b
                MOD(r6, r5) # c or b
                r7 = ref() # a -> c or b

            r8 = ORR(c, b) # b -> c or b
            r9 = r_join_cases(r7, r8) # a or b -> c or b
            return MOD(r9, r2) # c or b

    raise RuleError()

@rule
def r_iff_or_right(r1: Ref, r2: Ref):
    """
    a <-> c, b or a |- b or c
    """
    match formula(r1), formula(r2):
        case (LogicConnective(name=const.IFF, args=[a, c]),
              LogicConnective(name=const.OR, args=[b, a1])) if a1 == a:
            with Context():
                r3 = ASM(a)
                r4 = r_iff_imp(r1)  # a -> c
                r5 = MOD(r4, r3)  # c
                r6 = ORR(b, c)  # c -> b or c
                MOD(r6, r5)  # c or b
                r7 = ref()  # a -> b or c

            r8 = ORL(b, c)  # b -> b or c
            r9 = r_join_cases(r8, r7)  # b or a -> b or c
            return MOD(r9, r2)  # b or c

    raise RuleError()

@rule
def r_iff_and_left(r1: Ref, r2: Ref):
    """
    a <-> c, a and b |- c and b
    """
    match formula(r1), formula(r2):
        case (LogicConnective(name=const.IFF, args=[a, c]),
              LogicConnective(name=const.AND, args=[a1, b])) if a1 == a:
            r_a = r_and_left(r2) # a
            r_b = r_and_right(r2) # b
            r_c = r_iff_mod(r1, r_a) # c
            return r_and(r_c, r_b)

    raise RuleError()

@rule
def r_to_not_not(r1: Ref):
    """
    p |- ~~p
    """
    r2 = tau.p_to_not_not_p(formula(r1))
    return MOD(r2, r1)

@rule
def r_not_not_to(r1: Ref):
    """
    ~~p |- p
    """
    not_not_p = formula(r1)
    match not_not_p:
        case LogicConnective(name=const.NEG, args=[LogicConnective(name=const.NEG, args=[p])]):
            r2 = tau.not_not_p_to_p(p)
            return MOD(r2, r1)

    raise RuleError()

@rule
def r_proof_p_by_not_p(r1: Ref):
    """
    (~p -> p) |- p
    """
    f = formula(r1)
    match f:
        case LogicConnective(name=const.IMP, args=[not_p, p]) if not_p == Not(p):
            r2 = tau.p_to_p(p) # p -> p
            return r_join_exclusive_cases(r2, r1) # p

    raise RuleError()

@rule
def r_inv_imp(r1: Ref):
    """
    p -> q |- ~q -> ~p
    """
    f = formula(r1)
    match f:
        case LogicConnective(name=const.IMP, args=[p, q]):
            r2 = tau.imp_inv(p, q)
            return MOD(r2, r1)

    raise RuleError()

@rule
def r_de_morgan_neg_con(r1: Ref):
    """
    ~(p and q) |- ~p or ~q
    """
    f = formula(r1)
    match f:
        case LogicConnective(name=const.NEG, args=[LogicConnective(name=const.AND, args=[p, q])]):
            r2 = tau.de_morgan_not_and_to_or_not(p, q)
            return MOD(r2, r1)

    raise RuleError()

@rule
def r_de_morgan_dis_neg(r1: Ref):
    """
    ~p or ~q |- ~(p and q)
    """
    f = formula(r1)
    match f:
        case LogicConnective(
            name=const.OR,
            args=[
                LogicConnective(name=const.NEG, args=[p]),
                LogicConnective(name=const.NEG, args=[q]),
            ],
        ):
            r2 = tau.de_morgan_or_not_to_not_and(p, q)
            return MOD(r2, r1)

    raise RuleError()

@rule
def r_de_morgan_neg_dis(r1: Ref):
    """
    ~(p or q) |- ~p and ~q
    """
    f = formula(r1)
    match f:
        case LogicConnective(name=const.NEG, args=[LogicConnective(name=const.OR, args=[p, q])]):
            r2 = tau.de_morgan_not_or_to_and_not(p, q)
            return MOD(r2, r1)

    raise RuleError()


@rule
def r_de_morgan_con_neg(r1: Ref):
    """
    ~p and ~q |- ~(p or q)
    """
    f = formula(r1)
    match f:
        case LogicConnective(
            name=const.AND,
            args=[
                LogicConnective(name=const.NEG, args=[p]),
                LogicConnective(name=const.NEG, args=[q]),
            ],
        ):
            r2 = tau.de_morgan_and_not_to_not_or(p, q)
            return MOD(r2, r1)

    raise RuleError()

@rule
def r_imp_to_dis(r1: Ref):
    """
    p -> q |- ~p or q
    """
    f = formula(r1)
    match f:
        case LogicConnective(name=const.IMP, args=[p, q]):
            with Context():
                r3 = ASM(p) # p
                r4 = MOD(r1, r3) # q
                r_or_right(Not(p), r4)
                r5 = ref() # p -> ~p or q

            r6 = ORL(Not(p), q) # ~p -> ~p or q
            return r_join_exclusive_cases(r5, r6)

    raise RuleError()

@rule
def r_dis_com(r1: Ref):
    """
    p or q |- q or p
    """
    match formula(r1):
        case LogicConnective(name=const.OR, args=[p, q]):
            r2 = ORR(q, p) # p -> q or p
            r3 = ORL(q, p) # q -> q or p
            r4 = r_join_cases(r2, r3) # p or q -> q or p
            return MOD(r4, r1)

    raise RuleError()

@rule
def r_con_com(r1: Ref):
    """
    p and q |- q and p
    """
    match formula(r1):
        case LogicConnective(name=const.AND, args=[p, q]):
            r2 = r_and_left(r1) # p
            r3 = r_and_right(r1) # q
            return  r_and(r3, r2) # q and p

    raise RuleError()
