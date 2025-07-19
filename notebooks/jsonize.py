#%%
from reason.core.transform.jsonize import jsonize
from reason.core.language import Language
from reason.kernel import Kernel
from json import dumps

L = Language()
L.add_const("∅")
f_json = jsonize(L("∀a. ∃x. P(a, x, ∅) → Q(x, a) and R(x)"))

payload = {
    "type": "Command",
    "name": "ToCnf",
    "args": [f_json]
}

Kernel().run(dumps(payload))


