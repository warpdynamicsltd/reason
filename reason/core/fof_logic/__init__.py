from reason.kernel.proof import *

def p_implies_p(p: FirstOrderFormula) -> int:
    imp  = IMP(p, p)                              # p→p→p
    con  = CON(p, p)                              # ¬p→p→p
    lem  = LEM(p)                                 # p∨¬p
    dis  = DIS(p, Not(p), Implies(p, p))          # big schema
    mp1  = MOD(dis, imp)                          # ¬p→p→p
    mp2  = MOD(mp1, con)                          # (p∨¬p)→p→p
    mp3  = MOD(mp2, lem)                          # p→p
    return mp3

def p_and_q(p_index: int, q_index: int) -> int:
    p_formula = formula(p_index)        # p
    q_formula = formula(q_index)        # q
    ax      = AND(p_formula, q_formula)     # p→q→p∧q
    mp1     = MOD(ax, p_index)              # q→p∧q
    mp2     = MOD(mp1, q_index)             # p∧q
    return mp2

def p_or_q(p_index: int, q_index: int) -> int:
    p_formula = formula(p_index)        # p
    q_formula = formula(q_index)        # q
    ax      = ORL(p_formula, q_formula)     # p→p∨q
    mp      = MOD(ax, p_index)              # p∨q
    return mp

def a_p_and_q(a_p_idx: int, a_q_idx: int) -> int:
    """
    Given indices of
        • a_p_idx :  a → p
        • a_q_idx :  a → q
    construct a proof of
        a → (p ∧ q)
    """
    # ------------------------------------------------------------------
    # 1.  Extract the common antecedent a and the consequents p , q
    # ------------------------------------------------------------------
    a_imp_p = formula(a_p_idx)           # a → p
    a_imp_q = formula(a_q_idx)           # a → q

    match (a_imp_p, a_imp_q):
        case (LogicConnective(name=const.IMP, args=[a1, p]),
              LogicConnective(name=const.IMP, args=[a2, q])) if a1 == a2:
            a = a1
        case _:
            raise RuntimeError("Premises must be implications having the same antecedent")

    # ------------------------------------------------------------------
    # 2.  Obtain p → q → p ∧ q   (∧–introduction axiom)
    # ------------------------------------------------------------------
    and_idx   = AND(p, q)                             # p → q → p∧q
    and_form  = formula(and_idx)

    # ------------------------------------------------------------------
    # 3.  Lift the axiom under the antecedent ‘a’
    #     We prove a → (p → q → p∧q)
    # ------------------------------------------------------------------
    imp_idx   = IMP(and_form, a)                      # (p→q→p∧q) → a → (p→q→p∧q)
    mp0_idx   = MOD(imp_idx, and_idx)                 # a → (p → q → p∧q)

    # ------------------------------------------------------------------
    # 4.  From a → p derive a → q → p∧q
    #     TRN : (a→(p→q→p∧q)) → ((a→p) → (a→q→p∧q))
    # ------------------------------------------------------------------
    trn1_idx  = TRN(a, p, Implies(q, And(p, q)))
    mp1_idx   = MOD(trn1_idx, mp0_idx)                # (a→p) → (a→q→p∧q)
    mp2_idx   = MOD(mp1_idx, a_p_idx)                 # a → q → p∧q

    # ------------------------------------------------------------------
    # 5.  Combine with a → q to obtain a → p∧q
    #     TRN : (a→(q→p∧q)) → ((a→q) → (a→p∧q))
    # ------------------------------------------------------------------
    trn2_idx  = TRN(a, q, And(p, q))
    mp3_idx   = MOD(trn2_idx, mp2_idx)                # (a→q) → (a→p∧q)
    result    = MOD(mp3_idx, a_q_idx)                 # a → p∧q

    return result
