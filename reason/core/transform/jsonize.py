from reason.core.fof_types import FirstOrderFormula
from reason.core.transform.transformer import Transformer

class JSONizer(Transformer):
    def variable(self, obj, name):
        return dict(type="Variable", name=name)

    def const(self, obj, name):
        return dict(type="Const", name=name)

    def function(self, obj, name, args, targs):
        return dict(type="Function", name=name, args=targs)

    def predicate(self, obj, name, args, targs):
        return dict(type="Predicate", name=name, args=targs)

    def logic_connective(self, obj, name, args, targs):
        return dict(type="LogicConnective", name=name, args=targs)

    def logic_quantifier(self, obj, name, args, targs):
        return dict(type="LogicQuantifier", name=name, args=targs)


def jsonize(formula: FirstOrderFormula) -> dict:
    return JSONizer(formula).result