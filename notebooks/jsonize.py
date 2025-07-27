#%%
from json import dumps, loads

from reason.core.transform.jsonize import jsonize
from reason.core.transform.from_json import from_json
from reason.core.fof_types import *
from reason.core.language import Language
from reason.kernel import Kernel
from reason.kernel.proof import *
from reason.core.theory.tautology import prove
from reason.parser.tptp import TPTPParser

L = Language()
L.add_const("a")

# parser = TPTPParser()
#
#
# proof_obj = prove(L("(∀x.∀y. P(x, y)) → P(a, a)"))
#
# formulas = {}
# for item in proof_obj["proof"]:
#     if item["formula"] == "$false":
#         continue
#     print(item)
#     formulas[item["id"]] = parser(item["formula"])
#     print(L.printer(parser(item["formula"])))
#
#
# print(L.printer(Kernel.to_ennf(formulas[3])))
# print(L.printer(Kernel.to_cnf(formulas[4])))

# print(dumps(proof_obj, indent=2))

# print(jsonize(L("x=x")))

proof = Proof()
proof.add(lem(L("P")))
proof.add(imp(L("P or ~P"), L("Q")))
proof.add(mod(1, 0))

print(L.printer(proof.formula()))

# f_in = L("(∀x. P(x, z)) → P(z, z)")
# #
# f = Kernel.substitute("z", Function("f", Variable("u"), Variable("b")), f_in)
# f = Kernel.substitute("z", Const("a"), f_in)
# print(L.printer(f))
#
# print(Kernel.is_simple_axiom(L("P → Q")))
#
# f = Kernel.skolemize(f_in)
# print(L.printer(f))


