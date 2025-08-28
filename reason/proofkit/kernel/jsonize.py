from reason.core.transform.jsonize import JSONizer
from reason.core.fof_types import FirstOrderFormula

class ProofKitJSONizer(JSONizer):
    def const(self, obj, name):
        if name[:8] == "context_":
            return dict(type="ContextConst", name=int(name[8:]))
        return dict(type="Const", name=name)

def jsonize(formula: FirstOrderFormula):
    return ProofKitJSONizer(formula).result

