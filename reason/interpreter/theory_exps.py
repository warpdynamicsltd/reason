from beartype import beartype

from reason.parser.tree import AbstractSyntaxTree


@beartype
def assert_formula(self, formula_ast: AbstractSyntaxTree):
    formula = self.theory.formula(formula_ast)
    self.theory.add_formula(formula)
    self.log("info", "assertion", formula=formula, ast=formula_ast)


@beartype
def assume_formula(self, formula_ast: AbstractSyntaxTree):
    formula = self.theory.formula(formula_ast)
    self.log("info", "assumption", formula=formula, ast=formula_ast)
    self.theory.add_atomic_axiom(formula)
