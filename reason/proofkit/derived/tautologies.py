from reason.core.fof_ops import And, Implies, Not, Or
from reason.core.fof_types import FirstOrderFormula
from reason.proofkit.derived.rules import r_and_left, r_and_right, r_join_cases, r_and, r_contradiction, \
    r_join_exclusive_cases
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import Context, ASM, IFI, MOD, ref, formula, CON, LEM, ORL, ORR


def iff_tau(a: FirstOrderFormula, b: FirstOrderFormula) -> Ref:
    """
    (a → b) ∧ (b → a) → (a ⟷ b)
    """
    with Context():
        r1 = ASM(And(Implies(a, b), Implies(b, a)))
        r2 = IFI(a, b)
        r3 = r_and_left(r1)
        r4 = r_and_right(r1)
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
            r3 = ref()
        assert formula(r3) == Implies(p, p)
        with Context():
            r4 = ASM(Not(p))
            r5 = CON(Not(p), p) # ~~p -> (~p -> p)
            r6 = MOD(r5, r1) # ~p -> p
            MOD(r6, r4) # p
            r7 = ref()
        assert formula(r7) == Implies(Not(p), p)
        r8 = r_join_cases(r3, r7) # p or ~p -> p
        r9 = LEM(p)
        r10 = MOD(r8, r9)
    return r10


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
        r8 = r_join_cases(r7, r3) # ~p or ~~p -> ~~p
        r9 = LEM(Not(p))
        r10 = MOD(r8, r9)
    return r10


def de_morgan_not_and_to_or(p: FirstOrderFormula, q: FirstOrderFormula):
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
                r4 = r_and(r2, r3) # p and q
                r5 = r_contradiction(r4, r0, Or(Not(p), Not(q))) # ~p or ~q
                r6 = ref() # q -> ~p or ~q
            r7 = ORR(Not(p), Not(q))  # ~q -> ~p or ~q
            r_join_exclusive_cases(r6, r7) # ~p or ~q
            r8 = ref() # p -> ~p or ~q

        return r_join_exclusive_cases(r8, r1)


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
                r_contradiction(r5, r2, Not(a)) # ~a
                r6 = ref() # a -> ~a
            r_join_exclusive_cases(r6, r3) # ~a
            r7 = ref() # ~b -> ~a
        return ref() # (a -> b) -> (~b -> ~a)


def imp_trans(a: FirstOrderFormula, b: FirstOrderFormula, c: FirstOrderFormula):
    """
    (a -> b) and (b -> c) -> (a -> c)
    """
    with Context():
        r1 = ASM(And(Implies(a, b), Implies(b, c))) # (a -> b) and (b -> c)
        r3 = r_and_left(r1) # (a -> b)
        r5 = r_and_right(r1) # (b -> c)
        with Context():
            r6 = ASM(a) # a
            r7 = MOD(r3, r6) # b
            MOD(r5, r7) # c
        return ref()
