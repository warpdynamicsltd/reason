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

global PROOF

L = Language()
BEGIN(L)

r1 = p_iff_not_not_p(L("P(x)"))
with Context():
    r2 = ASM(L("∀x. P(x)"))
    r3 = r_iff_to_all(r1, r2, "x")
print(PROOF.to_ctxproof())
f = RETURN()