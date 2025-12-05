from unittest import case

from reason.core.transform.transformer import Transformer
from reason.proofkit.derived.qty_rules import *

from reason.proofkit.derived.rules import *
from reason.proofkit.derived.tautologies import *
from reason.proofkit.kernel.proof import *


def iff_right(f: FirstOrderFormula) -> FirstOrderFormula:
    match f:
        case LogicConnective(name=const.IFF, args=[a, b]):
            return b

    raise RuntimeError()


class ProvedTransformer:
    def __init__(self, f: FirstOrderFormula):
        self.result = self._transform(f)

    @classmethod
    def outer(cls, method):
        def wrapper(self, *args):
            r1 = method(self, *args)  # method.__name__(*args) <-> X
            X = iff_right(formula(r1))
            r2 = self._transform(X)  # X <-> T(X)
            return r_iff_trans(r1, r2) # method.__name__(*args) <-> T(X)
        return wrapper

    @classmethod
    def inner(cls, method):
        def wrapper(self, *args):
            return method(self, *map(self._transform, args))
        return wrapper # method.__name__(*args) <-> method.__name__(*[T(a) for a in args])

    @classmethod
    def inner_quant(cls, method):
        def wrapper(self, a, x):
            return method(self, self._transform(a), x)

        return wrapper

    def neg(self, a: FirstOrderFormula):
        """
        @outer
        Returns:
            reference of ~a <-> T(X)

        @inner
        Return:
            reference of ~a <-> ~T(a)

        """
        pass

    def con(self, a: FirstOrderFormula, b: FirstOrderFormula):
        pass

    def dis(self, a: FirstOrderFormula, b: FirstOrderFormula):
        pass

    def imp(self, a: FirstOrderFormula, b: FirstOrderFormula):
        pass

    def iff(self, a: FirstOrderFormula, b: FirstOrderFormula):
        pass

    def all(self, a: FirstOrderFormula, x: str):
        pass

    def exists(self, a: FirstOrderFormula, x: str):
        pass

    def _transform(self, f: FirstOrderFormula):
        """
        Args:
            f: FirstOrderFormula - formula to be transformed

        Returns:
            Reference of proved tautology f <-> T(f)

        """
        match f:
            case Predicate():
                return p_iff_p(f)

            case LogicConnective(name=const.NEG, args=[a]):
                return self.neg(a)

            case LogicConnective(name=const.AND, args=[a, b]):
                return self.con(a, b)

            case LogicConnective(name=const.OR, args=[a, b]):
                return self.dis(a, b)

            case LogicConnective(name=const.IMP, args=[a, b]):
                return self.imp(a, b)

            case LogicConnective(name=const.IFF, args=[a, b]):
                return self.iff(a, b)

            case LogicQuantifier(name=const.EXISTS, args=[var, arg]):
                return self.exists(arg, var.name)

            case LogicQuantifier(name=const.FORALL, args=[var, arg]):
                return self.all(arg, var.name)

        raise RuntimeError()


class IDNProvedTransformer(ProvedTransformer):
    @ProvedTransformer.inner
    def neg(self, a):
        return r_iff_neg(a)

    @ProvedTransformer.inner
    def con(self, a, b):
        return r_iff_and(a, b)

    @ProvedTransformer.inner
    def dis(self, a, b):
        return r_iff_or(a, b)

    @ProvedTransformer.inner
    def imp(self, a, b):
        return r_iff_imp(a, b)

    @ProvedTransformer.inner
    def iff(self, a, b):
        return r_iff_iff(a, b)

    @ProvedTransformer.inner_quant
    def exists(self, a, x: str):
        return r_iff_exists(a, x)

    @ProvedTransformer.inner_quant
    def all(self, a, x: str):
        return r_iff_all(a, x)


class ImpDisProvedTransformer(IDNProvedTransformer):
    @ProvedTransformer.outer
    def imp(self, a, b):
        r = dis_imp(a, b)  # (~a or b) <-> (a -> b)
        return r_iff_revolve(r) # (a -> b) <-> (~a or b)


class NnfProvedTransformer(IDNProvedTransformer):
    @ProvedTransformer.inner
    def neg_simple(self, a):
        return r_iff_neg(a)

    @ProvedTransformer.outer
    def neg_neg(self, a):
        match a:
            case LogicConnective(name=const.NEG, args=[b]):
                r1 = p_iff_not_not_p(b)  # b <-> ~~b
                return r_iff_revolve(r1) # ~~b <-> b

        raise RuntimeError()

    @ProvedTransformer.outer
    def neg_and(self, a):
        match a:
            case LogicConnective(name=const.AND, args=[p, q]):
                return de_morgan_neg_con_iff_dis_neg(p, q) # ~(p and q) <-> ~p or ~q


        raise RuntimeError()

    @ProvedTransformer.outer
    def neg_or(self, a):
        match a:
            case LogicConnective(name=const.OR, args=[p, q]):
                return de_morgan_neg_dis_iff_con_neg(p, q) # ~(p or q) <-> ~p and ~q

        raise RuntimeError()

    @ProvedTransformer.outer
    def neg_imp(self, a):
        match a:
            case LogicConnective(name=const.IMP, args=[p, q]):
                r1 = dis_imp(p, q) # ~p or q <-> (p -> q)
                r2 = r_iff_revolve(r1) # (p -> q) <-> ~p or q
                return r_iff_neg(r2) # ~(p -> q) <-> ~(~p or q)

        raise RuntimeError()

    @ProvedTransformer.outer
    def neg_iff(self, a):
        match a:
            case LogicConnective(name=const.IFF, args=[p, q]):
                r1 = iff_iff(p, q)  # (p -> q and p -> q) <-> (p <-> q)
                r2 = r_iff_revolve(r1) # (p <-> q) <-> (p -> q and p -> q)
                return r_iff_neg(r2)  # ~(p -> q) <-> ~(p -> q and p -> q)

        raise RuntimeError()

    def neg(self, a):
        match a:
            case LogicConnective(name=const.NEG):
                return self.neg_neg(a)
            case LogicConnective(name=const.AND):
                return self.neg_and(a)
            case LogicConnective(name=const.OR):
                return self.neg_or(a)
            case LogicConnective(name=const.IMP):
                return self.neg_imp(a)
            case LogicConnective(name=const.IFF):
                return self.neg_iff(a)

        return self.neg_simple(a)

    @ProvedTransformer.outer
    def imp(self, a, b):
        r = dis_imp(a, b)  # (~a or b) <-> (a -> b)
        return r_iff_revolve(r)  # (a -> b) <-> (~a or b)

    @ProvedTransformer.outer
    def iff(self, a, b):
        r = iff_iff(a, b) # (a -> b and b -> a) <-> (a <-> b)
        return r_iff_revolve(r) # (a <-> b) <-> (a -> b and b -> a)


