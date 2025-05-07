from reason.core.fof_types import FirstOrderFormula

from reason.core.transform.base import make_bound_variables_unique, closure
from reason.core.transform.graph.formula import FormulaToGraphLab


def signature(formula: FirstOrderFormula):
    return FormulaToGraphLab(make_bound_variables_unique(closure(formula))).signature


def formula_sha256(formula: FirstOrderFormula):
    return FormulaToGraphLab(make_bound_variables_unique(closure(formula))).sha256
