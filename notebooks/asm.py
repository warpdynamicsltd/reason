#%%
from reason.core.language import Language
from reason.kernel.proof import *
from reason.core.fof_logic import *

L = Language()

BEGIN()
a_index = p_implies_p(L("P and Q"))
p_index = ANL(L("P"), L("Q"))
q_index = ANR(L("P"), L("Q"))
a_p_and_q(p_index, q_index)
f = END()
print(L.printer(f))

# BEGIN()
# a = LEM(L("P"))
# b = IMP(GET_FORMULA(a), L("Q"))
# print(b, a)
# print(L.printer(GET_FORMULA(b)))
# print(L.printer(GET_FORMULA(a)))
# c = MOD(b, a)
# f = END()
# print(L.printer(f))
# print(L.printer(GET_FORMULA(c)))