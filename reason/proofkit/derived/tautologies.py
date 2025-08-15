from reason.core.fof_ops import And, Implies, Not, Or
from reason.core.fof_types import FirstOrderFormula
import reason.proofkit.derived.rules as rules
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import *


def iff_tau(a: FirstOrderFormula, b: FirstOrderFormula) -> Ref:
    """
    (a → b) ∧ (b → a) → (a ⟷ b)
    """
    with Context():
        r1 = ASM(And(Implies(a, b), Implies(b, a)))
        r2 = IFI(a, b)
        r3 = rules.r_and_left(r1)
        r4 = rules.r_and_right(r1)
        r5 = MOD(r2, r3)
        MOD(r5, r4)
        return ref()


def not_not_p_to_p(p: FirstOrderFormula):
    """
    ~~p -> p
    """
    with Context():
        r1 = ASM(Not(Not(p)))
        with Context():
            r2 = ASM(p)
            r3 = ref() # p -> p

        with Context():
            r4 = ASM(Not(p))
            r5 = CON(Not(p), p) # ~~p -> (~p -> p)
            r6 = MOD(r5, r1) # ~p -> p
            MOD(r6, r4) # p
            r7 = ref() # ~p -> p

        r8 = rules.r_join_cases(r3, r7) # p or ~p -> p
        r9 = LEM(p)
        r10 = MOD(r8, r9)
        return ref()


def p_to_not_not_p(p: FirstOrderFormula):
    """
    p -> ~~p
    """
    with Context():
        r1 = ASM(p)
        with Context():
            r2 = ASM(Not(Not(p)))
            r3 = ref()
        assert formula(r3) == Implies(Not(Not(p)), Not(Not(p)))
        with Context():
            r4 = ASM(Not(p))
            r5 = CON(p, Not(Not(p))) # ~p -> (p -> ~~p)
            r6 = MOD(r5, r4) # p -> ~~p
            MOD(r6, r1) # ~~p
            r7 = ref()
        assert formula(r7) == Implies(Not(p), Not(Not(p)))
        r8 = rules.r_join_cases(r7, r3) # ~p or ~~p -> ~~p
        r9 = LEM(Not(p))
        r10 = MOD(r8, r9)
        return ref()

def p_iff_not_not_p(p: FirstOrderFormula):
    """
    p <-> ~~p
    """
    with Context():
        r1 = p_to_not_not_p(p) # p -> ~~p
        r2 = not_not_p_to_p(p) # ~~p -> p
        r3 = rules.r_and(r1, r2)
        r4 = iff_tau(p, Not(Not(p)))
        MOD(r4, r3)
        return ref()


def de_morgan_not_and_to_or_not(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~(p and q) -> ~p or ~q
    """
    with Context():
        r0 = ASM(Not(And(p, q))) # ~(p and q)
        r1 = ORL(Not(p), Not(q))  # ~p -> ~p or ~q
        with Context():
            r2 = ASM(p)
            with Context():
                r3 = ASM(q)
                r4 = rules.r_and(r2, r3) # p and q
                r5 = rules.r_contradiction(r4, r0, Or(Not(p), Not(q))) # ~p or ~q
                r6 = ref() # q -> ~p or ~q
            r7 = ORR(Not(p), Not(q))  # ~q -> ~p or ~q
            rules.r_join_exclusive_cases(r6, r7) # ~p or ~q
            r8 = ref() # p -> ~p or ~q

        rules.r_join_exclusive_cases(r8, r1)
        return ref()

def de_morgan_or_not_to_not_and(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~p or ~q -> ~(p and q)
    """
    with Context():
        r1 = ANL(p, q) # p and q -> p
        r2 = ANR(p, q) # p and q -> q
        r3 = imp_inv(And(p, q), p) # (p and q -> p) -> (~p -> ~(p and q))
        r4 = imp_inv(And(p, q), q) # (p and q -> q) -> (~q -> ~(p and q))
        r5 = MOD(r3, r1) # ~p -> ~(p and q)
        r6 = MOD(r4, r2) # ~q -> ~(p and q)
        rules.r_join_cases(r5, r6) # ~p or ~q -> ~(p and q)
        return ref()

def de_morgan_neg_con_iff_dis_neg(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~(p and q) <-> ~p or ~q
    """
    with Context():
        r1 = de_morgan_not_and_to_or_not(p, q)
        r2 = de_morgan_or_not_to_not_and(p, q)
        rules.r_imp_imp_iff(r1, r2)
        return ref()

def de_morgan_not_or_to_and_not(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~(p or q) -> ~p and ~q
    """
    with Context():
        r1 = ASM(Not(Or(p, q)))
        with Context():
            r2 = ASM(Not(Not(p))) # ~~p
            r3 = rules.r_not_not_to(r2) # p
            r4 = rules.r_or_left(r3, q) # p or q
            rules.r_contradiction(r4, r1, Not(p))
            r5 = ref() # ~~p -> ~p

        r6 = rules.r_proof_p_by_not_p(r5) # ~p

        with Context():
            r7 = ASM(Not(Not(q))) # ~~q
            r8 = rules.r_not_not_to(r7) # q
            r9 = rules.r_or_right(p, r8) # p or q
            rules.r_contradiction(r9, r1, Not(q))
            r10 = ref() # ~~q -> ~q

        r10 = rules.r_proof_p_by_not_p(r10) # ~q

        rules.r_and(r6, r10)
        return ref()

def de_morgan_and_not_to_not_or(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~p and ~q -> ~(p or q)
    """
    with Context():
        r0 = ASM(And(Not(p), Not(q))) # ~p and ~q
        r1 = rules.r_and_left(r0) # ~p
        r2 = rules.r_and_right(r0) # ~q
        with Context():
            r3 = ASM(p) # p
            rules.r_contradiction(r3, r1, Not(Or(p, q)))
            r4 = ref() # p -> ~(p or q)

        with Context():
            r5 = ASM(q) # q
            rules.r_contradiction(r5, r2, Not(Or(p, q)))
            r6 = ref() # q -> ~(p or q)

        r7 = rules.r_join_cases(r4, r6) # p or q -> ~(p or q)
        r8 = rules.r_inv_imp(r7) # ~~(p or q) -> ~(p or q)
        rules.r_proof_p_by_not_p(r8) # ~(p or q)
        return ref()

def de_morgan_neg_dis_iff_con_neg(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~(p or q) <-> ~p and ~q
    """
    with Context():
        r1 = de_morgan_not_or_to_and_not(p, q)
        r2 = de_morgan_and_not_to_not_or(p, q)
        rules.r_imp_imp_iff(r1, r2)
        return ref()

def p_to_p(p: FirstOrderFormula):
    """
    p -> p
    """
    with Context():
        ASM(p)
        r2 = ref()
    return r2


def imp_inv(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    (a -> b) -> (~b -> ~a)
    """
    with Context():
        r1 = ASM(Implies(a, b)) # a -> b
        with Context():
            r2 = ASM(Not(b)) # ~b
            r3 = p_to_p(Not(a)) # ~a -> ~a
            with Context():
                r4 = ASM(a) # a
                r5 = MOD(r1, r4)# b
                rules.r_contradiction(r5, r2, Not(a)) # ~a
                r6 = ref() # a -> ~a
            rules.r_join_exclusive_cases(r6, r3) # ~a
            r7 = ref() # ~b -> ~a
        return ref() # (a -> b) -> (~b -> ~a)


def imp_trans(a: FirstOrderFormula, b: FirstOrderFormula, c: FirstOrderFormula):
    """
    (a -> b) and (b -> c) -> (a -> c)
    """
    with Context():
        r1 = ASM(And(Implies(a, b), Implies(b, c))) # (a -> b) and (b -> c)
        r3 = rules.r_and_left(r1) # (a -> b)
        r5 = rules.r_and_right(r1) # (b -> c)
        with Context():
            r6 = ASM(a) # a
            r7 = MOD(r3, r6) # b
            MOD(r5, r7) # c
        return ref()
