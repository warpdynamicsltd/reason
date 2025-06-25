from beartype import beartype

from reason.core.fof_types import Const
from reason.parser.tree import AbstractSyntaxTree

def add_selection_axioms(self, formula_ast: AbstractSyntaxTree):
    context = self.current_context()
    formula, axioms = context.L.to_formula_and_required_axioms(formula_ast)
    for axiom in axioms:
        context.theory.add_atomic_axiom(axiom)
        self.log("info", "atomic axiom", formula=axiom, ast=formula_ast)

@beartype
def declare_consts(self, consts: tuple[str, ...]):
    context = self.current_context()
    for c in consts:
        context.declare(c)

@beartype
def define_formula(self, formula_ast: AbstractSyntaxTree):
    context = self.current_context()
    formula = context.define(formula_ast)
    self.log("info", "context definition", formula=formula, ast=formula_ast)
    return formula

@beartype
def declare_consts_with_constrain(self, formula_ast: AbstractSyntaxTree, consts: list[str]):
    context = self.current_context()
    formula = context.declare_consts_with_constrain(formula_ast, consts)
    self.log("info", "context definition", formula=formula, ast=formula_ast)
    return formula

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
def conclude_formula(self, formula_ast: AbstractSyntaxTree, auto_skip=False):
    context = self.current_context()
    formula, status = context.conclude(formula_ast, auto_skip=auto_skip)
    self.log("info", f"context conclusion {status.name}", formula=formula, ast=formula_ast)
