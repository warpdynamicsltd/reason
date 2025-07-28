#%%
from reason.core.language import Language
from reason.kernel.proof import *

L = Language()

BEGIN()
a = LEM(L("P"))
b = IMP(GET_FORMULA(a), L("Q"))
print(b, a)
print(L.printer(GET_FORMULA(b)))
print(L.printer(GET_FORMULA(a)))
c = MOD(b, a)
f = END()
print(L.printer(f))
print(L.printer(GET_FORMULA(c)))