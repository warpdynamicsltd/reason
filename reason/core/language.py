from beartype import beartype
from typing import Tuple

from reason.parser import Parser
from reason.printer import Printer
from reason.core.fof_types import FirstOrderFormula
from reason.parser.tree import AbstractSyntaxTree
from reason.tools.math.transform import utf8_to_varname
from reason.core.fof import FormulaBuilder


class Language:
    def __init__(self, inspect=True):
        self.parser = Parser()
        self.printer = Printer(self.parser.ogc)
        self.consts = {}
        self.const_values = set()
        self.inspect = inspect

    def add_const(self, c: str, c_value=None):
        if c in self.consts:
            raise RuntimeError(f"const {c} already defined")

        if c_value is None:
            # c_value = f"c{utf8_to_varname(c)}"
            c_value = c

        if c_value in self.const_values:
            raise RuntimeError(f"const value {c_value} alrady in use")
        
        self.consts[c] = c_value
        self.const_values.add(c_value)
        # self.consts[c] = c
        # self.const_values.add(c)
        

    @beartype
    def to_formula_and_required_axioms(
        self, ast: AbstractSyntaxTree
    ) -> Tuple[FirstOrderFormula, list[FirstOrderFormula]]:
        builder = FormulaBuilder(ast, consts=self.consts)
        formula = builder.formula
        if self.inspect and not builder.well_formed():
            raise RuntimeError(f"{formula.show()} is not well formed")
        return formula, builder.axioms

    def to_formula(self, ast: AbstractSyntaxTree) -> FirstOrderFormula:
        formula, _ = self.to_formula_and_required_axioms(ast)
        return formula
    
    def __call__(self, text : str):
        ast = self.parser(text)
        formula, _ = self.to_formula_and_required_axioms(ast)
        return formula
    
    def display(self, call, formula):
        call(self.printer(formula))


def derive(L: Language) -> Language:
    resL = Language(inspect=L.inspect)
    resL.consts = dict(L.consts.items())
    return resL
