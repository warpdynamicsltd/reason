#%%
import json
from reason.core.language import Language
from reason.core.theory.tautology import prove
from reason.core.transform.describe import describe
from reason.proofkit.derived.transform import NnfProvedTransformer
from reason.proofkit.kernel.proof import *
from reason.core.transform.base import quantifier_signature, remove_universal_quantifiers

L = Language()
# L.add_const("a")

# formula = L("a ∪ (p ∩ q) = (a ∪ p) ∩ (a ∪ q)")
# print(remove_universal_quantifiers(formula))
# L.display(print, formula)
#
# print(describe(formula))


obj = prove(L("( ∃y. ∀x. P(x, y) ) → ( ∀x. ∃y.  P(x, y) )"))

print(json.dumps(obj, indent=2))

BEGIN(L)
r1 = NnfProvedTransformer(f=L("( ∃y. ∀x. P(x, y) ) → ( ∀x. ∃y.  P(x, y) )")).result
res_f = PROOF()
print(L.printer(res_f))
# %%
