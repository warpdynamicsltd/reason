#%%
import importlib
import reason
from reason.core.fof_types import Variable
from reason.core.theory import Theory
from reason.vampire import Vampire
from reason.parser import Parser
from reason.printer import Printer
from reason.core.fof_types import LogicConnective
from reason.core.transform.skolem import prenex_normal_raw, prenex_normal, skolem, SkolemUniqueRepr
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    free_variables, closure



importlib.reload(reason.core.theory )

parser = Parser()
printer = Printer(parser.ogc)

vampire_prover = Vampire(verbose=False)
T = Theory(parser, vampire_prover)

#%%
list((1, 3, 4))

#%%
f = T.compile("∃x.∀u. A(x, u)")
g = T.compile("A → B")
print(f.to_tuple())
print(g.to_tuple())

print(g < f)
#print(int < float)

#%%
from collections import Counter

print(Counter([{1}, {3}, {4}]))

#%%
T.add_const('c')

print(T("P(c) → (∃x. P(x))"))

#%%
f = T.compile("∀x.∀y.∃u. B(x) ⟷ (∃z. P(y, u) ∨ Q(x, u))")
s = skolem(f)
print(printer(s))
print(SkolemUniqueRepr()(s).get_sorted())

#%%
print(free_variables(T.compile("∀u. A(x, u) → (B(o) → (U(z))) ")))

#%%
print(T.prover(LogicConnective('IFF', f, prenex_normal(f))))


#%%
f = T.compile("~(∀x.∃u. P)")
print(f.show())
print(printer(prenex_normal_raw(f)))

#%%
f = T.formula_builder(parser("∀x.∀y.∃u. B(x) → (∃z. P(y, u))"))

f1 = f.replace(Variable('x'), Variable('z'))
print(f1.show())
g, sign = quantifier_signature(f)
print(g, sign)

p = prepend_quantifier_signature(g, list(sign))
print(p == f)

#%%
f = T.compile("C ∧ (A ⟷ B)")
tf = expand_iff(f)

print(tf.show())
print(printer(UniqueVariables()(tf)))

#%%
f = T.formula_builder(parser("∀x, u. ∃y. P(x) ∧ (Q(u) ∨ R) → (∃z. A(y) ∧ ~B(z))"))
print(f.show())

print(printer(f))

# print(T.formula_builder.well_formed(f))

#%%
print(parser.ogc.create_lark_code())

#%%
[0].appendleft(1)