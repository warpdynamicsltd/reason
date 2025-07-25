from reason.core.fof_types import *
from reason.core.transform.jsonize import jsonize
import reason.kernel

class Axiom:
    def __init__(self, label : str, formulas : list[FirstOrderFormula], axiom_formula: FirstOrderFormula):
        self.label = label
        self.formulas = formulas
        self.axiom_formula = axiom_formula

    def to_json(self):
        return dict(type="Axiom", name=self.label, args=[list(map(jsonize, self.formulas)), jsonize(self.axiom_formula)])


class Rule:
    def __init__(self, label: str, indices : list[int], formula: FirstOrderFormula):
        self.label = label
        self.indices = indices
        self.formula = formula

    def to_json(self):
        return dict(type="Rule", name=self.label, args=[self.indices, jsonize(self.formula)])

class Proof:
    def __init__(self):
        self.proof = []

    def add(self, element: Axiom | Rule):
        self.proof.append(element)

    def to_json(self):
        return dict(type="Proof", name="", args=list(map(lambda obj: obj.to_json(), self.proof)))

    def is_valid(self):
        try:
            return reason.kernel.Kernel.is_valid_proof(self)
        except reason.kernel.KernelError:
            return False