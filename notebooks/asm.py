#%%
from reason.core.language import Language
from reason.kernel.proof import *

L = Language()

begin()
a = lem(L("P"))
b = imp(L("P or ~P"), L("Q"))
mod(b, a)
f = end()
print(L.printer(f))