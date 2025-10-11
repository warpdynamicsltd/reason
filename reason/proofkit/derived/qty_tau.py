from reason.core.fof_ops import And, Implies, Not, Or
from reason.core.fof_types import FirstOrderFormula
import reason.proofkit.derived.rules as rules
import reason.proofkit.derived.qty_rules as qty_rules
import reason.proofkit.derived.tautologies as tau
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

def exists_over_imp(a: FirstOrderFormula, b: FirstOrderFormula, x: str):
    """
    ( ∀x. b(x) -> a ) -> ( ( ∃x. b(x) ) -> a )
    """
    with Context():
        r1 = ASM(Forall(x, Implies(b, a)))
        with Context():
            r2 = ASM(Exists(x, b))
            sk = get_next_skolem_const_name()
            r3 = SKO(r2, sk) # b(sk)
            r4 = ALL(Implies(b, a), Const(sk), x) # ( ∀x. b(x) -> a ) -> ( b(sk) -> a )
            r5 = MOD(r4, r1) # b(sk) -> a
            MOD(r5, r3) # a
            # ( ∃x. b(x) ) -> a
        return ref()

def de_morgan_not_exists_to_all_not(p: FirstOrderFormula, x: str):
    """
    ~ ( ∃x. p(x) ) -> ∀x. ~p(x)
    """
    with Context():
        r0 = ASM(Not(Exists(x, p)))
        c = get_context_const_name()
        with Context():
            r1 = ASM(Not(Not(p.replace(Variable(x), Const(c))))) # ~~p(c)
            r2 = rules.r_not_not_to(r1) # p(c)
            r3 = EXT(p, Const(c), x) # p(c) -> ( ∃x. p(x) )
            r4 = MOD(r3, r2) # ∃x. p(x)
            rules.r_contradiction(r4, r0, Not(formula(r2))) # ~p(c)
            r5 = ref() # ~~p(c) -> ~p(c)
        r6 = rules.r_proof_p_by_not_p(r5) # ~p(c)
        r7 = CTV(r6, c, x) # ~p(x)
        GEN(r7, x) # ∀x. ~p(x)
        return ref()

def de_morgan_all_not_to_not_exist(p: FirstOrderFormula, x: str):
    """
    ∀x. ~p(x) -> ~ ( ∃x. p(x) )
    """
    with Context():
        r1 = ASM(Forall(x, Not(p)))
        with Context():
            r2 = ASM(Not(Not(Exists(x, p)))) # ~~∃x. p(x)
            r3 = rules.r_not_not_to(r2) # ∃x. p(x)
            sk = get_next_skolem_const_name()
            r4 = SKO(r3, sk) # p(sk)
            r5 = ALL(Not(p), Const(sk), x) # (∀x. ~p(x)) -> ~p(sk)
            r6 = MOD(r5, r1) # ~p(sk)
            rules.r_contradiction(r4, r6, Not(Exists(x, p))) # ~ ( ∃x. p(x) )
            r6 = ref() # ~~( ∃x. p(x) ) -> ~ ( ∃x. p(x) )
        rules.r_proof_p_by_not_p(r6) # ~ ( ∃x. p(x) )
        return ref() # ∀x. ~p(x) -> ~ ( ∃x. p(x) )

def de_morgan_exists_not_to_not_all(p: FirstOrderFormula, x: str):
    """
    ∃x. ~p(x) -> ~( ∀x. p(x) )
    """
    with Context():
        r1 = ASM(Exists(x, Not(p))) # ∃x. ~p(x)
        sk = get_next_skolem_const_name()
        r2 = SKO(r1, sk) # ~p(sk)
        with Context():
            r3 = ASM(Not(Not(Forall(x, p)))) # ~~ ∀x. p(x)
            r4 = rules.r_not_not_to(r3) # ∀x. p(x)
            r5 = ALL(p, Const(sk), x) # ∀x. p(x) -> p(sk)
            r6 = MOD(r5, r4) # p(sk)
            r7 = rules.r_contradiction(r6, r2, Not(Forall(x, p))) # ~ ∀x. p(x)
            r8 = ref() # ( ~~ ∀x. p(x) ) -> (~ ∀x. p(x))
        rules.r_proof_p_by_not_p(r8) # ~∀x. p(x)
        return ref()

def de_morgan_not_all_to_exists_not(p: FirstOrderFormula, x: str):
    """
    ~( ∀x. p(x) ) -> ∃x. ~p(x)
    """
    with Context():
        r1 = ASM(Not(Forall(x, p))) # ~( ∀x. p(x) )
        with Context():
            r2 = ASM(Not(Exists(x, Not(p)))) # ~( ∃x. ~p(x) )
            r3 = de_morgan_not_exists_to_all_not(Not(p), x) # ~( ∃x. ~p(x) ) -> ( ∀x. ~~p(x) )
            r4 = MOD(r3, r2) # ( ∀x. ~~p(x) )
            r5 = tau.p_iff_not_not_p(p) # p(x) <-> ~~p(x)
            r6 = rules.r_iff_revolve(r5) # ~~p(x) <-> p(x)
            r7 = qty_rules.r_iff_all(r6, r4, x) # ∀x. p(x)
            rules.r_contradiction(r7, r1, Exists(x, Not(p))) # ∃x. ~p(x)
            r8 = ref() # ~( ∃x. ~p(x) ) -> ∃x. ~p(x)
        rules.r_proof_p_by_not_p(r8) # ∃x. ~p(x)
        return ref()


def de_morgan_not_exists_iff_all_not(p: FirstOrderFormula, x: str):
    """
    ~ ( ∃x. p(x) ) <-> ∀x. ~p(x)
    """
    r1 = de_morgan_not_exists_to_all_not(p, x)
    r2 = de_morgan_all_not_to_not_exist(p, x)
    return rules.r_imp_imp_iff(r1, r2)


def de_morgan_exists_not_iff_not_all(p: FirstOrderFormula, x: str):
    """
    ∃x. ~p(x) <-> ~( ∀x. p(x) )
    """
    r1 = de_morgan_exists_not_to_not_all(p, x)
    r2 = de_morgan_not_all_to_exists_not(p, x)
    return rules.r_imp_imp_iff(r1, r2)