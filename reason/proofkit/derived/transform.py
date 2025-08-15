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
                r_iff_and_left(r1, r2) # a and c
                r4 = ref() # a and b -> c and b
            with Context():
                r5 = ASM(And(c, b))
                r6 = r_iff_revolve(r1) # c <-> a
                r_iff_and_left(r6, r5) # a and b
                r8 = ref()

            return r_imp_imp_iff(r4, r8)

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
