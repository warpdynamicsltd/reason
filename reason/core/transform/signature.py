from reason.core.fof import FirstOrderFormula

from reason.core.transform.base import make_bound_variables_unique, closure
from reason.core.transform.graph.skolem import SkolemFormulaToGraphLab
from reason.core.transform.graph.formula import FormulaToGraphLab


def formula_sha256(formula: FirstOrderFormula):
    return FormulaToGraphLab(closure(make_bound_variables_unique(formula))).sha256
