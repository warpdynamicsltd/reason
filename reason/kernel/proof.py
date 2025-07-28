from reason.core.fof_types import *
from reason.core.fof_ops import *
from reason.parser.tree.consts import *
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
        self.formulas = []

    def add(self, element: Axiom | Rule, formula: FirstOrderFormula = None):
        self.proof.append(element)
        self.formulas.append(formula)

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
        res, formula = func(*args, **kwargs)
        PROOF.add(res, formula)
        return len(PROOF.proof) - 1

    return wrapper

def BEGIN():
    PROOF.clear()

def END():
    return PROOF.formula()

def GET_FORMULA(index: int):
    return PROOF.formulas[index]

@asm
def LEM(a: FirstOrderFormula):
    return Axiom("LEM", [a], []), Or(a, Not(a))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IMP", [a, b], []), Implies(a, Implies(b, a))

@asm
def LEM(a: FirstOrderFormula):
    return Axiom("LEM", [a], []), Or(a, Not(a))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IMP", [a, b], []), Implies(a, Implies(b, a))

@asm
def TRN(a: FirstOrderFormula, b1: FirstOrderFormula, b2: FirstOrderFormula):
    return Axiom("TRN", [a, b1, b2], []), Implies(Implies(a, Implies(b1, b2)), Implies(Implies(a, b1), Implies(a, b2)))

@asm
def ANL(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ANL", [a, b], []), Implies(And(a, b), a)

@asm
def ANR(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ANR", [a, b], []), Implies(And(a, b), b)

@asm
def AND(a: FirstOrderFormula, b: FirstOrderFormula):  # Named "and_axiom" to avoid conflicts with "and" keyword
    return Axiom("AND", [a, b], []), Implies(a, Implies(b, And(a, b)))

@asm
def ORL(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ORL", [a, b], []), Implies(a, Or(a, b))

@asm
def ORR(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ORR", [a, b], []), Implies(b, Or(a, b))

@asm
def DIS(a: FirstOrderFormula, b: FirstOrderFormula, c: FirstOrderFormula):
    return Axiom("DIS", [a, b, c], []), Implies(Implies(a, c), Implies(Implies(b, c), Implies(Or(a, b), c)))

@asm
def CON(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("CON", [a, b], []), Implies(Not(a), Implies(a, b))

@asm
def ALL(a: FirstOrderFormula, t: Term, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term must be a variable")
    return Axiom("ALL", [a], [t, v]), Implies(Forall(v, a), a.replace(v, t))

@asm
def EXT(a: FirstOrderFormula, t: Term, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term must be a variable")
    return Axiom("EXT", [a], [t, v]), Implies(a.replace(v, t), Exists(v, a))

@asm
def ALH(a: FirstOrderFormula, b: FirstOrderFormula, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term is not a variable")
    return Axiom("ALH", [a, b], [v]), Implies(Forall(v, Implies(a, b)), Implies(a, Forall(v, b)))

@asm
def EXH(a: FirstOrderFormula, b: FirstOrderFormula, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term is not a variable")
    return Axiom("EXH", [a, b], [v]), Implies(Forall(v, Implies(b, a)), Implies(Exists(v, b), a))

@asm
def MOD(a: int, b: int):
    formula_a = PROOF.formulas[a]
    formula_b = PROOF.formulas[b]
    match formula_a:
        case LogicConnective(name=const.IMP, args=[x, y]) if x == formula_b:
            return Rule("MOD", [a, b], []), y

    raise RuntimeError("Invalid formulas")