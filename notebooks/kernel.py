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