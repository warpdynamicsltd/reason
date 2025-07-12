#%%
from reason.core.transform.jsonize import jsonize
from reason.core.language import Language
from reason.kernel import Kernel
from json import dumps

L = Language()
L.add_const("∅")
payload = dumps(jsonize(L("∀x. P(x, ∅) → Q(x) and R(x)")), indent=2)

Kernel().run(payload)


