#%%
from reason.core.language import Language
from reason.kernel import Kernel
from reason.kernel.proof import *
from reason.kernel.statement import *
from reason.core.fof_logic import *

L = Language()

BEGIN()
with Block():
    r1 = ASM(L("P")) # P
    with Block():
        r2 = ASM(L("Q")) # Q
        IDN(r1); # P
        r3 = ref()
    assert formula(r3) == L("Q → P")
    r4 = ref()
assert formula(r4) == L("P → (Q → P)")
f = RETURN()
print(L.printer(f))

BEGIN()
with Block():
    r1 = ASM(L("P → (Q1 → Q2)"))
    with Block():
        r2 = ASM(L("P → Q1"))
        with Block():
            r3 = ASM(L("P"))
            r4 = MOD(r2, r3)
            assert formula(r4) == L("Q1")
            r5 = MOD(r1, r3)
            assert formula(r5) == L("Q1 → Q2")
            r6 = MOD(r5, r4)
            assert formula(r6) == L("Q2")
            r7 = ref()
        assert formula(r7) == L("P → Q2")
        r8 = ref()
    assert formula(r8) == L("(P → Q1) → (P → Q2)")
    r9 = ref()

f = RETURN()
print(L.printer(f))

BEGIN()
with Block():
    r1 = ASM(L("(A → B) ∧ (B → C)"))
    r2 = ANL(L("A → B"), L("B → C"))
    r3 = MOD(r2, r1)
    assert formula(r3) == L("A → B")
    r4 = ANR(L("A → B"), L("B → C"))
    r5 = MOD(r4, r1)
    assert formula(r5) == L("B → C")
    with Block():
        r6 = ASM(L("A"))
        r7 = MOD(r3, r6)
        assert formula(r7) == L("B")
        r8 = MOD(r5, r7)
        assert formula(r8) == L("C")
        r9 = ref()
    assert formula(r9) == L("A → C")
    r10 = ref()

f = RETURN()
print(L.printer(f))

def r_and_left(p: Ref):
    match formula(p):
        case LogicConnective(name=const.AND, args=[a, b]):
            r = ANL(a, b)
            return MOD(r, p)
        case _:
            raise RuntimeError("non and formula")

def r_and_right(p: Ref):
    match formula(p):
        case LogicConnective(name=const.AND, args=[a, b]):
            r = ANR(a, b)
            return MOD(r, p)
        case _:
            raise RuntimeError("non and formula")

def r_and(a: Ref, b: Ref):
    r1 = AND(formula(a), formula(b)) # a -> (b -> (a and b))
    r2 = MOD(r1, a) # (b -> (a and b))
    return MOD(r2, b)




BEGIN()
with Block():
    r1 = ASM(L("(A → B) ∧ (B → C)"))
    r3 = r_and_left(r1)
    assert formula(r3) == L("A → B")
    r5 = r_and_right(r1)
    assert formula(r5) == L("B → C")
    with Block():
        r6 = ASM(L("A"))
        r7 = MOD(r3, r6)
        assert formula(r7) == L("B")
        r8 = MOD(r5, r7)
        assert formula(r8) == L("C")
        r9 = ref()
    assert formula(r9) == L("A → C")
    r10 = ref()

f = RETURN()
print(L.printer(f))

BEGIN()
with Block():
    r1 = ASM(L("(A → B) ∧ (B → A)"))
    r2 = IFI(L("A"), L("B"))
    assert formula(r2) == L(("(A → B) → ((B → A) → (A ⟷ B))"))
    r3 = r_and_left(r1)
    assert formula(r3) == L("A → B")
    r4 = r_and_right(r1)
    assert formula(r4) == L("B → A")
    r5 = MOD(r2, r3)
    assert formula(r5) == L("(B → A) → (A ⟷ B)")
    r6 = MOD(r5, r4)
    r10 = ref()

f = RETURN()
print(L.printer(f))

def iff_tau(a: FirstOrderFormula, b: FirstOrderFormula) -> Ref:
    """
    (a → b) ∧ (b → a) → (a ⟷ b)
    """
    with Block():
        r1 = ASM(And(Implies(a, b), Implies(b, a)))
        r2 = IFI(a, b)
        r3 = r_and_left(r1)
        r4 = r_and_right(r1)
        r5 = MOD(r2, r3)
        MOD(r5, r4)
        return ref()

BEGIN()
r1 = iff_tau(L("A"), L("B"))
r2 = IFO(L("A"), L("B"))
r3 = iff_tau(L("(A → B) ∧ (B → A)"), L("A ⟷ B"))
r5 = r_and(r1, r2)
MOD(r3, r5)
f = RETURN()
print(L.printer(f))

def join_cases(case1: Ref, case2: Ref):
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

def join_exclusive_cases(case1: Ref, case2: Ref):
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

def not_not_p_to_p(p: FirstOrderFormula):
    """
    ~~p -> p
    """
    with Block():
        r1 = ASM(Not(Not(p)))
        with Block():
            r2 = ASM(p)
            r3 = ref()
        assert formula(r3) == Implies(p, p)
        with Block():
            r4 = ASM(Not(p))
            r5 = CON(Not(p), p) # ~~p -> (~p -> p)
            r6 = MOD(r5, r1) # ~p -> p
            MOD(r6, r4) # p
            r7 = ref()
        assert formula(r7) == Implies(Not(p), p)
        r8 = join_cases(r3, r7) # p or ~p -> p
        r9 = LEM(p)
        r10 = MOD(r8, r9)
    return r10

def p_to_not_not_p(p: FirstOrderFormula):
    """
    p -> ~~p
    """
    with Block():
        r1 = ASM(p)
        with Block():
            r2 = ASM(Not(Not(p)))
            r3 = ref()
        assert formula(r3) == Implies(Not(Not(p)), Not(Not(p)))
        with Block():
            r4 = ASM(Not(p))
            r5 = CON(p, Not(Not(p))) # ~p -> (p -> ~~p)
            r6 = MOD(r5, r4) # p -> ~~p
            MOD(r6, r1) # ~~p
            r7 = ref()
        assert formula(r7) == Implies(Not(p), Not(Not(p)))
        r8 = join_cases(r7, r3) # ~p or ~~p -> ~~p
        r9 = LEM(Not(p))
        r10 = MOD(r8, r9)
    return r10

def contradiction(a: Ref, b: Ref, outcome: FirstOrderFormula):
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

def de_morgan_not_and_to_or(p: FirstOrderFormula, q: FirstOrderFormula):
    """
    ~(p and q) -> ~p or ~q
    """
    with Block():
        r0 = ASM(Not(And(p, q))) # ~(p and q)
        r1 = ORL(Not(p), Not(q))  # ~p -> ~p or ~q
        with Block():
            r2 = ASM(p)
            with Block():
                r3 = ASM(q)
                r4 = p_and_q(r2, r3) # p and q
                r5 = contradiction(r4, r0, Or(Not(p), Not(q))) # ~p or ~q
                r6 = ref() # q -> ~p or ~q
            r7 = ORR(Not(p), Not(q))  # ~q -> ~p or ~q
            join_exclusive_cases(r6, r7) # ~p or ~q
            r8 = ref() # p -> ~p or ~q

        return join_exclusive_cases(r8, r1)

def p_to_p(p: FirstOrderFormula):
    with Block():
        ASM(p)
        r2 = ref()
    return r2

def imp_inv(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    (a -> b) -> (~b -> ~a)
    """
    with Block():
        r1 = ASM(Implies(a, b)) # a -> b
        with Block():
            r2 = ASM(Not(b)) # ~b
            r3 = p_to_p(Not(a)) # ~a -> ~a
            with Block():
                r4 = ASM(a) # a
                r5 = MOD(r1, r4)# b
                contradiction(r5, r2, Not(a)) # ~a
                r6 = ref() # a -> ~a
            join_exclusive_cases(r6, r3) # ~a
            r7 = ref() # ~b -> ~a
        return ref() # (a -> b) -> (~b -> ~a)





BEGIN()
r = not_not_p_to_p(L("P"))
f = RETURN()
print(L.printer(f))

BEGIN()
r = p_to_not_not_p(L("P"))
f = RETURN()
print(L.printer(f))

BEGIN()
r = de_morgan_not_and_to_or(L("P"), L("Q"))
f = RETURN()
print(L.printer(f))

BEGIN()
r = p_to_p(L("P"))
f = RETURN()
print(L.printer(f))

BEGIN()
r = imp_inv(L("P"), L("Q"))
f = RETURN()
print(L.printer(f))

