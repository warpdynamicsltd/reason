from typing import Self

from reason.core.fof_ops import *
from reason.parser.tree.consts import *

from reason.core.fof_types import FirstOrderFormula, Term, Variable, LogicConnective
from reason.proofkit.kernel.jsonize import jsonize
from reason.core.language import Language
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
        """
        get formula at given ref
        """
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

    def get_next_skolem_name(self):
        return f"skolem_{'_'.join(map(str, self.get_next_ref().indices))}"

    def get_depth(self):
        return len(self.ref.indices)

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
LANGUAGE: Language | None = None

def BEGIN(language: Language = None):
    global CURRENT, PROOF, LANGUAGE
    CURRENT = Block()
    PROOF = CURRENT
    LANGUAGE = language

class Context():
    def __enter__(self):
        global CURRENT, PROOF

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

def get_context_const_name():
    const_name = f"context_{CURRENT.get_depth()}"
    LANGUAGE.add_const(const_name)
    return const_name

def get_next_skolem_const_name():
    skolem_name = CURRENT.get_next_skolem_name()
    LANGUAGE.add_const(skolem_name)
    return skolem_name

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
    """
    a or ~a
    """
    return Axiom("LEM", [a], [], Or(a, Not(a)))

@asm
def IMP(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    a -> (b -> a)
    """
    return Axiom("IMP", [a, b], [], Implies(a, Implies(b, a)))

# @asm
# def TRN(a: FirstOrderFormula, b1: FirstOrderFormula, b2: FirstOrderFormula):
#     """
#     (a -> (b1 -> b2)) -> ( (a -> b1) -> (a -> b2) )
#     """
#     return Axiom("TRN", [a, b1, b2], [], Implies(Implies(a, Implies(b1, b2)), Implies(Implies(a, b1), Implies(a, b2))))

@asm
def ANL(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    a and b -> a
    """
    return Axiom("ANL", [a, b], [], Implies(And(a, b), a))

@asm
def ANR(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    a and b -> b
    """
    return Axiom("ANR", [a, b], [], Implies(And(a, b), b))

@asm
def AND(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    a -> (b -> (a and b))
    """
    return Axiom("AND", [a, b], [], Implies(a, Implies(b, And(a, b))))

@asm
def ORL(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    a -> a or b
    """
    return Axiom("ORL", [a, b], [], Implies(a, Or(a, b)))

@asm
def ORR(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    b -> a or b
    """
    return Axiom("ORR", [a, b], [], Implies(b, Or(a, b)))

@asm
def DIS(a: FirstOrderFormula, b: FirstOrderFormula, c: FirstOrderFormula):
    """
    (a -> c) -> ((b -> c) -> (a or b -> c))
    """
    return Axiom("DIS", [a, b, c], [], Implies(Implies(a, c), Implies(Implies(b, c), Implies(Or(a, b), c))))

@asm
def CON(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    ~a -> (a -> b)
    """
    return Axiom("CON", [a, b], [], Implies(Not(a), Implies(a, b)))

@asm
def IFI(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    (a -> b) -> ((b -> a) -> (a <-> b))
    """
    return Axiom("IFI", [a, b], [], Implies(Implies(a, b), Implies(Implies(b, a), Iff(a, b))))

@asm
def IFO(a: FirstOrderFormula, b: FirstOrderFormula):
    """
    (a <-> b) -> (a -> b) and (b -> a)
    """
    return Axiom("IFO", [a, b], [], Implies(Iff(a, b), And(Implies(a, b), Implies(b, a))))

@asm
def ALL(a: FirstOrderFormula, t: Term, x: str):
    """
    ( ∀x. a(x) ) -> a(t)
    """
    v = Variable(x)
    return Axiom("ALL", [a], [t, v], Implies(Forall(x, a), a.replace(v, t)))

@asm
def EXT(a: FirstOrderFormula, t: Term, x: str):
    """
    a(t) -> ( ∃x. a(x) )
    """
    v = Variable(x)
    return Axiom("EXT", [a], [t, v], Implies(a.replace(v, t), Exists(x, a)))

# @asm
# def ALH(a: FirstOrderFormula, b: FirstOrderFormula, x: str):
#     """
#     ( ∀x. (a -> b(x)) ) -> ( a -> ∀x. b(x) )
#     """
#     v = Variable(x)
#     return Axiom("ALH", [a, b], [v], Implies(Forall(x, Implies(a, b)), Implies(a, Forall(x, b))))
#
# @asm
# def EXH(a: FirstOrderFormula, b: FirstOrderFormula, x: str):
#     """
#     ( ∀x. (b(x) -> a) ) -> ( (∃x. b(x)) -> a )
#     """
#     v = Variable(x)
#     return Axiom("EXH", [a, b], [v], Implies(Forall(x, Implies(b, a)), Implies(Exists(x, b), a)))

### RULES ###

@asm
def MOD(r1: Ref, r2: Ref):
    """
    p -> q, p |- q
    """
    formula_a = PROOF.value(r1)
    formula_b = PROOF.value(r2)
    match formula_a:
        case LogicConnective(name=const.IMP, args=[x, y]) if x == formula_b:
            return Rule("MOD", [r1, r2], [], y)

    raise RuntimeError("Invalid formulas")

@asm
def GEN(r: Ref, x: str):
    """
    p |- ∀x. p
    """
    return Rule("GEN", [r], [Variable(x)], Forall(x, PROOF.value(r)))

# | "CTV" -> (function [a], [ContextConst(index); Var(v)] -> substitute_context_const_in_formula_by_var index v a | _ -> failwith "illformed rule")
@asm
def CTV(a: Ref, context_const_name: str, x: str):
    """
    p(context_i) |- p(x)
    """
    c = Const(context_const_name)
    return Rule("CTV", [a], [c, Variable(x)], PROOF.value(a).replace(c, Variable(x)))

@asm
def SKO(a: Ref, skolem_const_name: str):
    """
    ∃x. p(x) |- p(skolem_ref)
    """
    f = PROOF.value(a)
    match f:
        case LogicQuantifier(name=const.EXISTS, args=[var, p]):
            c = Const(skolem_const_name)
            return Rule("SKO", [a], [c, var], p.replace(var, c))

    raise RuntimeError("Invalid formula")

@asm
def IDN(a: Ref):
    """
    p |- p
    """
    formula_a = PROOF.value(a)
    return Rule("IDN", [a], [], formula_a)
