#%%
import json
from reason.core.language import Language
from reason.core.theory.tautology import prove

L = Language()
L.add_const("a")

obj = prove(L("P(a)"), [L("∀x. P(x) ∧ Q(x)")])

print(json.dumps(obj, indent=2))
# %%
