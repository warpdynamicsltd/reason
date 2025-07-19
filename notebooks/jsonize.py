#%%
from json import dumps, loads

from reason.core.transform.jsonize import jsonize
from reason.core.transform.from_json import from_json
from reason.core.fof_types import *
from reason.core.language import Language
from reason.kernel import Kernel
from reason.core.theory.tautology import prove
from reason.parser.tptp import TPTPParser

L = Language()
L.add_const("a")

parser = TPTPParser()


proof_obj = prove(L("(∀x.∀y. P(x, y)) → P(a, a)"))

formulas = {}
for item in proof_obj["proof"]:
    if item["formula"] == "$false":
        continue
    print(item)
    formulas[item["id"]] = parser(item["formula"])
    print(L.printer(parser(item["formula"])))


print(L.printer(Kernel.to_ennf(formulas[3])))
print(L.printer(Kernel.to_cnf(formulas[4])))

# print(dumps(proof_obj, indent=2))



# f_in = L("∀a. ∃x. P(a, x, ∅) → Q(x, a) and R(x)")
#
# f = Kernel.to_cnf(f_in)
# print(L.printer(f))
#
# f = Kernel.skolemize(f_in)
# print(L.printer(f))


