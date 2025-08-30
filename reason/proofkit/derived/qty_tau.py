from reason.core.fof_ops import And, Implies, Not, Or
from reason.core.fof_types import FirstOrderFormula
import reason.proofkit.derived.rules as rules
from reason.proofkit.derived.rules import r_imp_imp_iff
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import *

def all_to_exist(p: FirstOrderFormula, x: str):
    """
    ( ∀x. p(x) ) -> ( ∃x. p(x) )
    """
    with Context():
        c = get_context_const_name()
        r1 = ASM(Forall(x, p)) # ∀x. P(x)
        r2 = ALL(p, Const(c), x) # (∀x. P(x)) -> P(c1)
        r3 = MOD(r2, r1) # P(c1)
        r4 = EXT(p, Const(c), x) # P(c1) -> ∃x. P(x)
        MOD(r4, r3) # ∃x. P(x)
        return ref() # ∀x. P(x) -> ∃x. P(x)

def all_over_imp(a: FirstOrderFormula, b: FirstOrderFormula, x: str):
    """
    ( ∀x. a -> b(x) ) -> ( a -> ( ∀x. b(x) ) )
    """
    with Context():
        r0 = ASM(Forall(x, Implies(a, b)))
        with Context():
            c = get_context_const_name()
            r1 = ASM(a)
            r2 = ALL(Implies(a, b), Const(c), x) # ( ∀x. a -> b(x) ) -> ( a -> b(c) )
            r3 = MOD(r2, r0) # a -> b(c)
            r4 = MOD(r3, r1) # b(c)
            r5 = CTV(r4, c, x) # b(x)
            GEN(r5, x) # ∀x. b(x)
            r6 = ref() # a -> ( ∀x. b(x) )
        return ref()