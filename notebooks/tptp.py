#%%
from lark import Transformer, Lark
from reason.vampire import Vampire
from reason.core import AbstractTerm
from reason.parser.tptp import TPTPTreeToAbstractSyntaxTree
from importlib.resources import files

from reason.parser import Parser
from reason.printer import Printer
from reason.core.theory import Theory

parser = Parser()
printer = Printer(parser.ogc)

vampire_prover = Vampire(verbose=False)
T = Theory(parser, vampire_prover)

#%%
with open(files("reason") / "assets" / "lark" / "tptp.lark") as f:
    code = f.read()
    parser = Lark(code, start="formula", lexer="basic")

# tree = parser.parse("(! [X3] : (p_empty(X3) <=> ! [X0] : ~p_IN(X0,X3)) & ! [X0] : (X0 != X6 => ? [X1] : (f_INTERSECT(X1,X0) = X6 & p_IN(X1,X0)))) => ! [X0] : (p_empty(X0) => X0 = X6)")
tree = parser.parse("![X] : ? [Y] : (p_A(X) | p_B(Y))")

f = TPTPTreeToAbstractSyntaxTree().transform(tree)
print(repr(f))
print(printer(f))
g = T.compile(printer(f))
print(g)
print(g == f)

# f = T.to_formula(ast_obj)
# print(f)
# print(printer(f))
