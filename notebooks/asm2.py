#%%
from reason.core.language import Language
from reason.core.fof_logic import *

L = Language()

def p_to_p(p: FirstOrderFormula):
    with Context():
        r1 = ASM(p)  # P
        r2 = IDN(r1);
        return ref()

BEGIN()
r = p_to_p(L("P"))
# P -> P
f = RETURN()

print(L.printer(f))

BEGIN()
with Context():
    r1 = ASM(L("P")) # P
    with Context():
        r2 = ASM(L("Q")) # Q
        IDN(r1); # P
        r3 = ref()
    assert formula(r3) == L("Q → P")
    r4 = ref()
assert formula(r4) == L("P → (Q → P)")
f = RETURN()
print(L.printer(f))




