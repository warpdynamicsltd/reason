from reason.core.fof_types import *
from reason.core.fof_ops import *
from reason.parser.tree.consts import *
from reason.kernel.statement import *
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

PROOF = None
CURRENT = None
def BEGIN():
    global CURRENT, PROOF
    CURRENT = None
    PROOF = None

class Block():
    def __enter__(self):
        global CURRENT, PROOF
        if CURRENT is None:
            CURRENT = BlockStmt()
            PROOF = CURRENT


        self.parent = CURRENT
        self.block = BlockStmt(ref=self.parent.get_next_ref())
        self.ref = None

        self.parent.add(self.block)
        CURRENT = self.block
        return self.block

    def __exit__(self, exc_type, exc_val, exc_tb):
        global CURRENT
        self.block.formula = self.block.get_formula()
        self.parent.formula = self.parent.get_formula()
        self.ref = self.block.ref
        CURRENT = self.parent
        return False

def ref():
    return reason.kernel.proof.CURRENT.ref

def asm(func):
    def wrapper(*args, **kwargs):
        global CURRENT
        res = func(*args, **kwargs)
        CURRENT.add(res)
        return CURRENT.statements[-1].ref

    return wrapper

def formula(ref: Ref):
    return PROOF.value(ref)

def RETURN():
    return reason.kernel.Kernel.prove_tautology(PROOF)
    # return PROOF.formula

@asm
def ASM(a: FirstOrderFormula):
    return Assumption(a)

@asm
def LEM(a: FirstOrderFormula):
    return AxiomStmt("LEM", [a], [], Or(a, Not(a)))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("IMP", [a, b], [], Implies(a, Implies(b, a)))

@asm
def LEM(a: FirstOrderFormula):
    return AxiomStmt("LEM", [a], [], Or(a, Not(a)))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("IMP", [a, b], [], Implies(a, Implies(b, a)))

@asm
def TRN(a: FirstOrderFormula, b1: FirstOrderFormula, b2: FirstOrderFormula):
    return AxiomStmt("TRN", [a, b1, b2], [], Implies(Implies(a, Implies(b1, b2)), Implies(Implies(a, b1), Implies(a, b2))))

@asm
def ANL(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("ANL", [a, b], [], Implies(And(a, b), a))

@asm
def ANR(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("ANR", [a, b], [], Implies(And(a, b), b))

@asm
def AND(a: FirstOrderFormula, b: FirstOrderFormula):  # Named "and_AxiomStmt" to avoid conflicts with "and" keyword
    return AxiomStmt("AND", [a, b], [], Implies(a, Implies(b, And(a, b))))

@asm
def ORL(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("ORL", [a, b], [], Implies(a, Or(a, b)))

@asm
def ORR(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("ORR", [a, b], [], Implies(b, Or(a, b)))

@asm
def DIS(a: FirstOrderFormula, b: FirstOrderFormula, c: FirstOrderFormula):
    return AxiomStmt("DIS", [a, b, c], [], Implies(Implies(a, c), Implies(Implies(b, c), Implies(Or(a, b), c))))

@asm
def CON(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("CON", [a, b], [], Implies(Not(a), Implies(a, b)))

@asm
def IFI(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("IFI", [a, b], [], Implies(Implies(a, b), Implies(Implies(b, a), Iff(a, b))))

@asm
def IFO(a: FirstOrderFormula, b: FirstOrderFormula):
    return AxiomStmt("IFO", [a, b], [], Implies(Iff(a, b), And(Implies(a, b), Implies(b, a))))

@asm
def ALL(a: FirstOrderFormula, t: Term, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term must be a variable")
    return AxiomStmt("ALL", [a], [t, v], Implies(Forall(v, a), a.replace(v, t)))

@asm
def EXT(a: FirstOrderFormula, t: Term, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term must be a variable")
    return AxiomStmt("EXT", [a], [t, v], Implies(a.replace(v, t), Exists(v, a)))

@asm
def ALH(a: FirstOrderFormula, b: FirstOrderFormula, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term is not a variable")
    return AxiomStmt("ALH", [a, b], [v], Implies(Forall(v, Implies(a, b)), Implies(a, Forall(v, b))))

@asm
def EXH(a: FirstOrderFormula, b: FirstOrderFormula, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term is not a variable")
    return AxiomStmt("EXH", [a, b], [v], Implies(Forall(v, Implies(b, a)), Implies(Exists(v, b), a)))

@asm
def MOD(a: Ref, b: Ref):
    formula_a = PROOF.value(a)
    formula_b = PROOF.value(b)
    match formula_a:
        case LogicConnective(name=const.IMP, args=[x, y]) if x == formula_b:
            return RuleStmt("MOD", [a, b], [], y)

    raise RuntimeError("Invalid formulas")

@asm
def IDN(a: Ref):
    formula_a = PROOF.value(a)
    return RuleStmt("IDN", [a], [], formula_a)