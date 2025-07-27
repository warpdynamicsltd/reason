from reason.core.fof_types import *
from reason.core.transform.jsonize import jsonize
import reason.kernel

class Axiom:
    def __init__(self, label : str, formulas : list[FirstOrderFormula], terms: list[Term]):
        self.label = label
        self.formulas = formulas
        self.terms = terms

    def to_json(self):
        return dict(type="Axiom", name=self.label, args=[list(map(jsonize, self.formulas)), list(map(jsonize, self.terms))])


class Rule:
    def __init__(self, label: str, indices : list[int], terms: list[Term]):
        self.label = label
        self.indices = indices
        self.terms = terms

    def to_json(self):
        return dict(type="Rule", name=self.label, args=[self.indices, list(map(jsonize, self.terms))])

class Proof:
    def __init__(self):
        self.proof = []

    def add(self, element: Axiom | Rule):
        self.proof.append(element)

    def clear(self):
        self.proof = []

    def to_json(self):
        return dict(type="Proof", name="", args=list(map(lambda obj: obj.to_json(), self.proof)))

    def formula(self):
        try:
            return reason.kernel.Kernel.final_tautology(self)
        except reason.kernel.KernelError:
            return False

PROOF = Proof()

def asm(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        PROOF.add(res)
        return len(PROOF.proof) - 1

    return wrapper

def begin():
    PROOF.clear()

def end():
    return PROOF.formula()

@asm
def lem(a: FirstOrderFormula):
    return Axiom("LEM", [a], [])

@asm
def imp(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IMP", [a, b], [])

@asm
def mod(a: int, b: int):
    return Rule("MOD", [a, b], [])