from reason.core.fof_ops import And, Implies, Not, Or
from reason.core.fof_types import FirstOrderFormula
import reason.proofkit.derived.rules as rules
from reason.proofkit.derived.rules import r_imp_imp_iff
from reason.proofkit.kernel import Ref
from reason.proofkit.kernel.proof import *

def all_to_exist(p: FirstOrderFormula, x: str):
    """
    ∀x. P(x) -> ∃x. P(x)
    """
    with Context():
        c = get_context_const_name()
        r1 = ASM(Forall(x, p)) # ∀x. P(x)
        r2 = ALL(p, Const(c), x) # (∀x. P(x)) -> P(c1)
        r3 = MOD(r2, r1) # P(c1)
        r4 = EXT(p, Const(c), x) # P(c1) -> ∃x. P(x)
        MOD(r4, r3) # ∃x. P(x)
        return ref() # ∀x. P(x) -> ∃x. P(x)