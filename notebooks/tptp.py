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

tree = parser.parse("! [X] : ? [Y, Z] : (p(f(X)) => (q(Y) & u(b)))")
f = TPTPTreeToAbstractSyntaxTree().transform(tree)
print(f)
print(printer(f))

# f = T.to_formula(ast_obj)
# print(f)
# print(printer(f))
