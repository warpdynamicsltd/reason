#%%

from reason.vampire.translator import to_tptp_fof
from reason.core.language import Language
from reason.proofkit.derived.tautologies import de_morgan_or_not_to_not_and, p_to_p, de_morgan_neg_con_iff_dis_neg, de_morgan_neg_dis_iff_con_neg
from reason.proofkit.derived.qty_tau import de_morgan_not_exists_to_all_not, de_morgan_exists_not_iff_not_all
from reason.proofkit.kernel.proof import *

L = Language()

#print(L.printer(L("p(x)")))

formula = L("p(x)")

global PROOF

BEGIN(L)
r = de_morgan_neg_dis_iff_con_neg(L("P"), L("Q"))
# r = de_morgan_not_exists_to_all_not(L("P"), "x")
# P -> P


print(PROOF.to_ctxproof())
f = RETURN()