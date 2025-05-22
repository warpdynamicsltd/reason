from beartype import beartype
from typing import Tuple

from reason.parser import Parser
from reason.core.fof_types import FirstOrderFormula
from reason.parser.tree import AbstractSyntaxTree
from reason.tools.math.transform import utf8_to_varname
from reason.core.fof import FormulaBuilder


class Language:
    def __init__(self, inspect=True):
        self.parser = Parser()
        self.consts = {}
        self.inspect = inspect

    def add_const(self, c: str):
        self.consts[c] = f"c{utf8_to_varname(c)}"

    @beartype
    def to_formula_and_required_axioms(
        self, ast: AbstractSyntaxTree
    ) -> Tuple[FirstOrderFormula, list[FirstOrderFormula]]:
        builder = FormulaBuilder(ast, consts=self.consts)
        formula = builder.formula
        if self.inspect and not builder.well_formed():
            raise RuntimeError(f"{formula.show()} is not well formed")
        return formula, builder.axioms
    
    def __call__(self, text : str):
        ast = self.parser(text)
        formula, _ = self.to_formula_and_required_axioms(ast)
        return formula
