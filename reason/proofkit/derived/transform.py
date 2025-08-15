from reason.proofkit.derived.rules import *
import reason.proofkit.derived.tautologies as tau
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import *

@rule
def t_iff_and_left(r1: Ref, b: FirstOrderFormula):
    """
    a <-> c |- a and b <-> c and b
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, c]):
            with Context():
                r2 = ASM(And(a, b))
                r_iff_and_left(r1, r2) # c and b
                r4 = ref() # a and b -> c and b
            with Context():
                r5 = ASM(And(c, b))
                r6 = r_iff_revolve(r1) # c <-> a
                r_iff_and_left(r6, r5) # a and b
                r8 = ref()

            return r_imp_imp_iff(r4, r8)

    raise RuleError()

@rule
def t_iff_and_right(r1: Ref, b: FirstOrderFormula):
    """
    a <-> c |- b and a <-> b and c
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, c]):
            with Context():
                r2 = ASM(And(b, a))
                r_iff_and_right(r1, r2) # b and c
                r4 = ref() # b and a -> b and c
            with Context():
                r5 = ASM(And(b, c)) # b and c
                r6 = r_iff_revolve(r1) # c <-> a
                r_iff_and_right(r6, r5) # b and a
                r8 = ref()

            return r_imp_imp_iff(r4, r8)

    raise RuleError()

@rule
def t_iff_or_left(r1: Ref, b: FirstOrderFormula):
    """
    a <-> c |- a or b <-> c or b
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, c]):
            with Context():
                r2 = ASM(Or(a, b))       # a or b
                r_iff_or_left(r1, r2)    # c or b
                r4 = ref()               # a or b -> c or b
            with Context():
                r5 = ASM(Or(c, b))       # c or b
                r6 = r_iff_revolve(r1)   # c <-> a
                r_iff_or_left(r6, r5)    # a or b
                r8 = ref()               # c or b -> a or b
            return r_imp_imp_iff(r4, r8)

    raise RuleError()


@rule
def t_iff_or_right(r1: Ref, b: FirstOrderFormula):
    """
    a <-> c |- b or a <-> b or c
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, c]):
            with Context():
                r2 = ASM(Or(b, a))        # b or a
                r_iff_or_right(r1, r2)    # b or c
                r4 = ref()                # b or a -> b or c
            with Context():
                r5 = ASM(Or(b, c))        # b or c
                r6 = r_iff_revolve(r1)    # c <-> a
                r_iff_or_right(r6, r5)    # b or a
                r8 = ref()                # b or c -> b or a
            return r_imp_imp_iff(r4, r8)

    raise RuleError()

@rule
def t_iff_neg(r1: Ref):
    """
    a <-> b |- ~a <-> ~b
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[a, b]):
            r2 = IFO(a, b)
            r3 = MOD(r2, r1) # a -> b and b -> a
            r4 = r_and_left(r3) # a -> b
            r5 = r_and_right(r3) # b -> a
            r6 = r_inv_imp(r4) # ~b -> ~a
            r7 = r_inv_imp(r5) # ~a -> ~b
            return r_imp_imp_iff(r7, r6)

    raise RuleError()

def t_imp_to_dis_atom(r: Ref):
    """
    if r = (p -> q) |- ~p or q
    else r
    """
    match formula(r):
        case LogicConnective(name=const.IMP):
            return r_imp_to_dis(r)
        case _:
            return r

def t_imp_to_dis(r: Ref):
    f = formula(r)
    match f:
        case Predicate():
            return r

        case LogicConnective(name=const.AND, args=[a, b]):
            pass
        case _:
            raise RuntimeError("non imp to dis")
