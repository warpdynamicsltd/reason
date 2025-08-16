from reason.core.transform.transformer import Transformer

from reason.proofkit.derived.rules import *
from reason.proofkit.derived.tautologies import *
from reason.proofkit.kernel.proof import *


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

def iff_right(f: FirstOrderFormula) -> FirstOrderFormula:
    match f:
        case LogicConnective(name=const.IFF, args=[a, b]):
            return b

    raise RuntimeError()

class TautologicalTransformer(Transformer):
    def neg(self, a, tau_a):
        return r_iff_neg(tau_a)

    def con(self, a, b, tau_a, tau_b):
        return r_iff_and(tau_a, tau_b)

    def dis(self, a, b, tau_a, tau_b):
        return r_iff_or(tau_a, tau_b)

    def imp(self, a, b, tau_a, tau_b):
        return r_iff_imp(tau_a, tau_b)

    def iff(self, a, b, tau_a, tau_b):
        return r_iff_iff(tau_a, tau_b)

    def predicate(self, obj, name, args, targs):
        return p_iff_p(obj)

    def logic_connective(self, obj, name, args, targs):
        match name:
            case const.NEG:
                return self.neg(args[0], targs[0])

            case const.AND:
                return self.con(args[0], args[1], targs[0], targs[1])

            case const.OR:
                return self.dis(args[0], args[1], targs[0], targs[1])

            case const.IMP:
                return self.imp(args[0], args[1], targs[0], targs[1])

            case const.IFF:
                return self.iff(args[0], args[1], targs[0], targs[1])

        raise RuntimeError()


    def logic_quantifier(self, obj, name, args, targs):
        pass

class ImpDisTransformer(TautologicalTransformer):
    def imp(self, a, b, tau_a, tau_b):
        F_a = iff_right(formula(tau_a))
        F_b = iff_right(formula(tau_b))
        r = r_iff_imp(tau_a, tau_b)  # (a -> b) <-> (F(a) -> F(b))
        r1 = dis_imp(F_a, F_b)  # (~F(a) or F(b)) <-> (F(a) -> F(b))
        r2 = r_iff_revolve(r1)  # (F(a) -> F(b)) <-> (~F(a) or F(b))
        return r_iff_trans(r, r2)  # (a -> b) <-> (~F(a) or F(b))



def t_imp_to_dis(f: FirstOrderFormula):
    match f:
        case Predicate():
            return p_iff_p(f)

        case LogicConnective(name=const.NEG, args=[a]):
            tau_a = t_imp_to_dis(a) # a <-> F(a)
            return r_iff_neg(tau_a) # ~a <-> ~F(a)

        case LogicConnective(name=const.AND, args=[a, b]):
            tau_a = t_imp_to_dis(a) # a <-> F(a)
            tau_b = t_imp_to_dis(b) # b <-> F(b)
            return r_iff_and(tau_a, tau_b) # a and b <-> F(a) and F(b)

        case LogicConnective(name=const.OR, args=[a, b]):
            tau_a = t_imp_to_dis(a)  # a <-> F(a)
            tau_b = t_imp_to_dis(b)  # b <-> F(b)
            return r_iff_or(tau_a, tau_b) # a or b <-> F(a) or F(b)

        case LogicConnective(name=const.IMP, args=[a, b]):
            tau_a = t_imp_to_dis(a)  # a <-> F(a)
            tau_b = t_imp_to_dis(b)  # b <-> F(b)
            F_a = iff_right(formula(tau_a))
            F_b = iff_right(formula(tau_b))
            r = r_iff_imp(tau_a, tau_b) # (a -> b) <-> (F(a) -> F(b))
            r1 = dis_imp(F_a, F_b) # (~F(a) or F(b)) <-> (F(a) -> F(b))
            r2 = r_iff_revolve(r1) # (F(a) -> F(b)) <-> (~F(a) or F(b))
            return r_iff_trans(r, r2) # (a -> b) <-> (~F(a) or F(b))

        case LogicConnective(name=const.IFF, args=[a, b]):
            tau_a = t_imp_to_dis(a)  # a <-> F(a)
            tau_b = t_imp_to_dis(b)  # b <-> F(b)
            return r_iff_iff(tau_a, tau_b)




    raise RuntimeError()
