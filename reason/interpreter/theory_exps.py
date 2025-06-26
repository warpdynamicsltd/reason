from beartype import beartype

from reason.parser.tree import AbstractSyntaxTree

def add_selection_axioms(self, formula_ast: AbstractSyntaxTree):
    formula, axioms = self.theory.get_langauge().to_formula_and_required_axioms(formula_ast)
    for axiom in axioms:
        self.theory.add_atomic_axiom(axiom)
        self.log("info", "atomic axiom", formula=axiom, ast=formula_ast)

def define_formula(self, formula_ast: AbstractSyntaxTree):
    formula = self.theory.formula(formula_ast)
    formula = self.theory.add_definition(formula)
    self.log("info", "definition", formula=formula, ast=formula_ast)
    return formula

@beartype
def declare_consts(self, consts: tuple[str, ...]):
    for c in consts:
        self.theory.declare_const(c)

@beartype
def declare_consts_with_constrain(self, formula_ast: AbstractSyntaxTree, consts: list[str]):
    for c in consts:
        self.theory.declare_const(c)
    formula = self.theory.formula(formula_ast)
    formula = self.theory.declare_consts_with_constrain(formula, consts)
    self.log("info", "definition", formula=formula, ast=formula_ast)
    return formula

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
