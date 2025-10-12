import reason.proofkit.derived.rules as rules
from reason.proofkit.kernel.proof import *

def r_gen_term(r1: Ref, x: str, t: Term):
    """
    p(x) |- p(t)
    """
    p = formula(r1)
    r2 = GEN(r1, x) # ∀x. p(x)
    r3 = ALL(p, t, x) # ( ∀x. p(x) ) -> p(t)
    return MOD(r3, r2)

def r_iff_to_all(r1: Ref, r2: Ref, x: str):
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

def r_iff_all(r1: Ref, x: str):
    """
    p(x) <-> q(x) |- ( ∀x. p(x) ) <-> ( ∀x. q(x) )
    """
    match formula(r1):
        case LogicConnective(name=const.IFF, args=[p, q]):
            with Context():
                r2 = ASM(Forall(x, p))
                r_iff_to_all(r1, r2, x) # ( ∀x. q(x) )
                r3 = ref() # ( ∀x. p(x) ) -> ( ∀x. q(x) )

            with Context():
                r4 = ASM(Forall(x, q))
                r5 = rules.r_iff_revolve(r1) # q(x) <-> p(x)
                r_iff_to_all(r5, r4, x) # ( ∀x. p(x) )
                r6 = ref() # ( ∀x. q(x) ) -> ( ∀x. q(x) )

            return rules.r_imp_imp_iff(r3, r6) # ( ∀x. p(x) ) <-> ( ∀x. q(x) )

    raise rules.RuleError()

def r_iff_to_exists(r1: Ref, r2: Ref, x: str):
    """
    p(x) <-> q(x), ∃x. p(x) |- ∃x. q(x)
    """
    match formula(r1), formula(r2):
        case (
            LogicConnective(name=const.IFF, args=[p, q]),
            LogicQuantifier(name=const.EXISTS, args=[var, p1]),
        ) if p == p1 and var == Variable(x):
            with Context():
                r3 = ASM(Exists(x, p))
                sk = get_next_skolem_const_name()
                r4 = SKO(r3, sk) # p(sk)
                r5 = r_gen_term(r1, x, Const(sk)) # p(sk) <-> q(sk)
                r6 = rules.r_iff_mod_left(r5, r4) # q(sk)
                r7 = EXT(q, Const(sk), x) # q(sk) -> ( ∃x. q(x) )
                MOD(r7, r6) # ( ∃x. q(x) )
                r8 = ref() # ( ∃x. p(x) ) -> ( ∃x. q(x) )
            return MOD(r8, r2) # ∃x. q(x)

    raise rules.RuleError()