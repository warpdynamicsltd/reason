from typing import Self

from reason.core.fof_ops import *
from reason.core.fof_types import FirstOrderFormula, Term, Variable, LogicConnective
from reason.parser.tree.consts import *
from reason.core.transform.jsonize import jsonize
import reason.proofkit.kernel

class Ref:
    def __init__(self, indices: list[int]):
        self.indices = tuple(indices)

    def to_json(self) -> dict:
        # { "type": "Ref", "name": None, "args": [ index ] }
        return {"type": "Ref", "name": None, "args": self.indices}

    def __repr__(self):
        return f"Ref({self.indices})"

class Assumption:
    def __init__(
            self,
            formula: FirstOrderFormula,
            ref: Ref = None,
    ):
        self.ref = ref
        self.formula = formula

    def to_json(self) -> dict:
        return {
            "type": "AssumptionStmt",
            "name": None,
            "args": [
                self.ref.to_json(),
                jsonize(self.formula),
            ],
        }


class Axiom:
    def __init__(
        self,
        label: str,
        fofs: list[FirstOrderFormula],
        terms: list[Term],
        formula: FirstOrderFormula,
        ref: Ref = None
    ):
        self.label = label
        self.fofs = fofs
        self.terms = terms
        self.formula = formula
        self.ref = ref

    def to_json(self) -> dict:
        return {
            "type": "AxiomStmt",
            "name": None,                      # label → name
            "args": [
                self.ref.to_json(),
                self.label,# 0  ref
                [jsonize(f) for f in self.fofs],     # 1  fofs
                [jsonize(t) for t in self.terms],    # 2  terms
                jsonize(self.formula),               # 3  formula
            ],
        }


class Rule:
    def __init__(
        self,
        label: str,
        refs: list[Ref],
        terms: list[Term],
        formula: FirstOrderFormula,
        ref: Ref = None,
    ):
        self.ref = ref
        self.label = label
        self.refs = refs
        self.terms = terms
        self.formula = formula

    def to_json(self) -> dict:
        return {
            "type": "RuleStmt",
            "name": None,
            "args": [
                self.ref.to_json(),
                self.label,
                [r.to_json() for r in self.refs],        # 1 refs
                [jsonize(t) for t in self.terms],        # 2 terms
                jsonize(self.formula),                   # 3 formula
            ],
        }


class Block:
    def __init__(
        self,
        statements: list[Axiom | Rule | Self] = [],
        formula: FirstOrderFormula = None,
        ref: Ref = Ref([]),
    ):
        self.ref = ref
        self.statements = list(statements)
        self.formula = formula

    def get_formula(self):
        if self.statements:
            if type(self.statements[0]) is Assumption:
                return Implies(self.statements[0].formula, self.statements[-1].formula)
            else:
                return self.statements[-1].formula
        else:
            return None

    def value(self, ref : Ref):
        index = ref.indices[0]
        statement = self.statements[index]
        if type(statement) is Block:
            if len(ref.indices) > 1:
                ref = Ref(list(ref.indices)[1:])
                return statement.value(ref)
            else:
                return statement.formula
        else:
            return statement.formula

    def get_next_ref(self):
        return Ref(list(self.ref.indices) + [len(self.statements)])

    def add(self, statement: Axiom | Rule | Self):
        statement.ref = self.get_next_ref()
        self.statements.append(statement)
        self.formula = self.get_formula()


    def to_json(self) -> dict:
        return {
            "type": "BlockStmt",
            "name": None,
            "args": [
                self.ref.to_json(),
                [s.to_json() for s in self.statements],
                jsonize(self.formula),
            ],
        }

PROOF : Block | None = None
CURRENT : Block | None = None

def BEGIN():
    global CURRENT, PROOF
    CURRENT = None
    PROOF = None

class Context():
    def __enter__(self):
        global CURRENT, PROOF
        if CURRENT is None:
            CURRENT = Block()
            PROOF = CURRENT


        self.parent = CURRENT
        self.block = Block(ref=self.parent.get_next_ref())
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
    return reason.proofkit.kernel.proof.CURRENT.ref

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
    return reason.proofkit.kernel.Kernel.prove_tautology(PROOF)
    # return PROOF.formula

@asm
def ASM(a: FirstOrderFormula):
    return Assumption(a)

@asm
def LEM(a: FirstOrderFormula):
    return Axiom("LEM", [a], [], Or(a, Not(a)))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IMP", [a, b], [], Implies(a, Implies(b, a)))

@asm
def LEM(a: FirstOrderFormula):
    return Axiom("LEM", [a], [], Or(a, Not(a)))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IMP", [a, b], [], Implies(a, Implies(b, a)))

@asm
def TRN(a: FirstOrderFormula, b1: FirstOrderFormula, b2: FirstOrderFormula):
    return Axiom("TRN", [a, b1, b2], [], Implies(Implies(a, Implies(b1, b2)), Implies(Implies(a, b1), Implies(a, b2))))

@asm
def ANL(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ANL", [a, b], [], Implies(And(a, b), a))

@asm
def ANR(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ANR", [a, b], [], Implies(And(a, b), b))

@asm
def AND(a: FirstOrderFormula, b: FirstOrderFormula):  # Named "and_AxiomStmt" to avoid conflicts with "and" keyword
    return Axiom("AND", [a, b], [], Implies(a, Implies(b, And(a, b))))

@asm
def ORL(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ORL", [a, b], [], Implies(a, Or(a, b)))

@asm
def ORR(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("ORR", [a, b], [], Implies(b, Or(a, b)))

@asm
def DIS(a: FirstOrderFormula, b: FirstOrderFormula, c: FirstOrderFormula):
    return Axiom("DIS", [a, b, c], [], Implies(Implies(a, c), Implies(Implies(b, c), Implies(Or(a, b), c))))

@asm
def CON(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("CON", [a, b], [], Implies(Not(a), Implies(a, b)))

@asm
def IFI(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IFI", [a, b], [], Implies(Implies(a, b), Implies(Implies(b, a), Iff(a, b))))

@asm
def IFO(a: FirstOrderFormula, b: FirstOrderFormula):
    return Axiom("IFO", [a, b], [], Implies(Iff(a, b), And(Implies(a, b), Implies(b, a))))

@asm
def ALL(a: FirstOrderFormula, t: Term, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term must be a variable")
    return Axiom("ALL", [a], [t, v], Implies(Forall(v, a), a.replace(v, t)))

@asm
def EXT(a: FirstOrderFormula, t: Term, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term must be a variable")
    return Axiom("EXT", [a], [t, v], Implies(a.replace(v, t), Exists(v, a)))

@asm
def ALH(a: FirstOrderFormula, b: FirstOrderFormula, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term is not a variable")
    return Axiom("ALH", [a, b], [v], Implies(Forall(v, Implies(a, b)), Implies(a, Forall(v, b))))

@asm
def EXH(a: FirstOrderFormula, b: FirstOrderFormula, v: Variable):
    if not isinstance(v, Variable):
        raise RuntimeError("Error: Term is not a variable")
    return Axiom("EXH", [a, b], [v], Implies(Forall(v, Implies(b, a)), Implies(Exists(v, b), a)))

@asm
def MOD(a: Ref, b: Ref):
    formula_a = PROOF.value(a)
    formula_b = PROOF.value(b)
    match formula_a:
        case LogicConnective(name=const.IMP, args=[x, y]) if x == formula_b:
            return Rule("MOD", [a, b], [], y)

    raise RuntimeError("Invalid formulas")

@asm
def IDN(a: Ref):
    formula_a = PROOF.value(a)
    return Rule("IDN", [a], [], formula_a)
