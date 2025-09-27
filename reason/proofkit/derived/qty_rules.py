import reason.proofkit.derived.rules as rules
from reason.proofkit.kernel.proof import *

def r_iff_all(r1: Ref, r2: Ref, x: str):
    """
    p(x) <-> q(x), ∀x. p(x) |- ∀x. q(x)
    """
    match formula(r1), formula(r2):
        case (
            LogicConnective(name=const.IFF, args=[p, q]),
            LogicQuantifier(name=const.FORALL, args=[var, p1]),
        ) if p == p1 and var == Variable(x):
            r3 = ALL(p, Variable(x), x) # (∀x. p(x)) -> p(x)
            r4 = MOD(r3, r2) # p(x)
            r5 = rules.r_iff_mod_left(r1, r4) # q(x)
            return GEN(r5, x) # ∀x. q(x)

    raise rules.RuleError()