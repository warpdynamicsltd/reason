from reason.core.fof_types import *
from reason.parser.tree.consts import *

def is_selection_axiom(formula: FirstOrderFormula):
    match formula:
        case LogicQuantifier(name=const.EXISTS, args=[v, f]):
            raise NotImplementedError()