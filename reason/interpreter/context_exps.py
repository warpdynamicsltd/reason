from beartype import beartype

from reason.parser.tree import AbstractSyntaxTree


@beartype
def declare_consts(self, consts: tuple[str, ...]):
    context = self.current_context()
    for c in consts:
        context.declare(c)


@beartype
def assert_formula(self, formula_ast: AbstractSyntaxTree):
    formula, status = self.current_context().add(formula_ast)
    self.log("info", f"context assertion {status.name}", formula=formula, ast=formula_ast)
    return status


@beartype
def assume_formula(self, formula_ast: AbstractSyntaxTree):
    context = self.current_context()
    formula = context.assume(formula_ast)
    self.log("info", "context assumption", formula=formula, ast=formula_ast)


@beartype
def conclude_formula(self, formula_ast: AbstractSyntaxTree):
    context = self.current_context()
    formula, status = context.conclude(formula_ast)
    self.log("info", f"context conclusion {status.name}", formula=formula, ast=formula_ast)
