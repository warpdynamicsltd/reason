#%%

from reason.vampire.translator import to_tptp_fof
from reason.core.language import Language
from reason.proofkit.derived.tautologies import de_morgan_or_not_to_not_and, p_to_p, de_morgan_neg_con_iff_dis_neg, de_morgan_neg_dis_iff_con_neg, p_iff_not_not_p, iff_iff
from reason.proofkit.derived.qty_tau import *
from reason.proofkit.derived.qty_rules import r_iff_to_all
from reason.proofkit.derived.transform import NnfProvedTransformer
from reason.proofkit.kernel.proof import *

L = Language()

#print(L.printer(L("p(x)")))

formula = L("p(x)")

#global PROOF

L = Language()
BEGIN(L)
# with Context():
#     r1 = ASM(L("∀x. P(x)"))
#     r2 = schema(p_iff_not_not_p, L("_Q"))
#     r3 = PSU(r2, L("_Q"), L("P(x)"))
#     r4 = r_iff_to_all(r3, r1, "x")
#r = all_over_imp(L("A(x)"), L("B(x)"), "x")
# r = iff_iff(L("A"), L("B"))
#r = p_iff_not_not_p(L("A"))
#r = de_morgan_not_exists_to_all_not(L("P(x)"), "x")
#r = de_morgan_not_all_to_exists_not(L("P(x)"), "x")
#r = p_iff_not_not_p(L("A"))
f_in = L("~( (∃x.∀y. P(x) ∧ K(x, y, z, u)) ⟷ (∀y. Q(y) ∧ (∃x.∀z.K(x, y, z, u))) )")
r = NnfProvedTransformer(f_in).result
print(len(PROOF.to_ctxproof()))
f = RETURN()
print(L.printer(f))