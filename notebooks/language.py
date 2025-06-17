#%%
import json
from reason.core.language import Language
from reason.core.theory.tautology import prove
from reason.core.transform.describe import describe
from reason.core.transform.base import quantifier_signature, remove_universal_quantifiers

L = Language()
# L.add_const("a")

formula = L("a ∪ (p ∩ q) = (a ∪ p) ∩ (a ∪ q)")
print(remove_universal_quantifiers(formula))
L.display(print, formula)

print(describe(formula))

# obj = prove(L("P(a)"), [L("∀x. P(x) ∧ Q(x)")])

# print(json.dumps(obj, indent=2))
# %%
