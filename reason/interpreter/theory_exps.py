from beartype import beartype

from reason.parser.tree import AbstractSyntaxTree


@beartype
def assert_formula(self, formula_ast: AbstractSyntaxTree):
    formula = self.theory.formula(formula_ast)
    formula, status = self.theory.add_formula(formula)
    self.log("info", f"assertion {status.name}", formula=formula, ast=formula_ast)
    return status


@beartype
def add_atomic_axiom_formula(self, formula_ast: AbstractSyntaxTree):
    formula = self.theory.formula(formula_ast)
    formula = self.theory.add_atomic_axiom(formula)
    self.log("info", "atomic axiom", formula=formula, ast=formula_ast)
