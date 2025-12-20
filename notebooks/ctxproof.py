#%%

from reason.vampire.translator import to_tptp_fof
from reason.core.language import Language
from reason.proofkit.derived.tautologies import de_morgan_or_not_to_not_and, p_to_p, de_morgan_neg_con_iff_dis_neg, de_morgan_neg_dis_iff_con_neg, p_iff_not_not_p
from reason.proofkit.derived.qty_tau import de_morgan_not_exists_to_all_not, de_morgan_exists_not_iff_not_all, exists_over_imp
from reason.proofkit.derived.qty_rules import r_iff_to_all
from reason.proofkit.kernel.proof import *

L = Language()

#print(L.printer(L("p(x)")))

formula = L("p(x)")

#global PROOF

L = Language()
BEGIN(L)
with Context():
    r1 = ASM(L("∀x. P(x)"))
    r2 = schema(p_iff_not_not_p, L("_Q"))
    r3 = PSU(r2, L("_Q"), L("P(x)"))
    r4 = r_iff_to_all(r3, r1, "x")
print(PROOF.to_ctxproof())
f = RETURN()
print(L.printer(f))