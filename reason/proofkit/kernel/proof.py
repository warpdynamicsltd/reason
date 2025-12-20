from typing import Self

from reason.core.fof_ops import *
from reason.parser.tree.consts import *
from reason.proofkit.kernel.ctxproof_tptp import to_tptp_fof

from reason.core.fof_types import FirstOrderFormula, Term, Variable, LogicConnective, Predicate, Const, Function
from reason.core.language import Language
from reason.core.transform.substitute import substitute_predicate
from reason.core.transform.transformer import Transformer
import reason.proofkit.kernel

from functools import cache

class Ref:
    last_id = 0
    references = {}

    def __init__(self, indices: list[int]):
        Ref.last_id += 1
        self.id = Ref.last_id
        self._indices = tuple(indices)
        self.statement = None
        Ref.references[self.id] = self

    @property
    def indices(self):
        """Compute indices dynamically based on parent statement chain"""
        if self.statement is None:
            # Fallback to stored indices if no statement is linked
            return self._indices

        # Build indices by traversing parent chain
        indices = []
        current = self.statement

        while current is not None and current.parent is not None:
            if current.index is not None:
                indices.insert(0, current.index)
            current = current.parent

        return tuple(indices)

    def to_ctxproof(self):
        if self.indices:
            return ".".join(map(str, self.indices))
        else:
            return "."

    def __repr__(self):
        return f"Ref({self.indices})"

class SkolemReplacer(Transformer):
    """Transformer that replaces skolem_<id> with skolem_<indices>"""

    def const(self, obj, name):
        if name.startswith("skolem_"):
            id_str = name.replace("skolem_", "")
            if id_str.isdigit():
                ref_id = int(id_str)
                if ref_id in Ref.references:
                    ref = Ref.references[ref_id]
                    new_name = f"skolem_{'_'.join(map(str, ref.indices))}"
                    return Const(new_name)
                else:
                    raise RuntimeError(f"Invalid skolem constant: {name}")
        return obj

    def function(self, obj, name, args, targs):
        if name.startswith("skolem_"):
            id_str = name.replace("skolem_", "")
            if id_str.isdigit():
                ref_id = int(id_str)
                if ref_id in Ref.references:
                    ref = Ref.references[ref_id]
                    new_name = f"skolem_{'_'.join(map(str, ref.indices))}"
                    return Function(new_name, *targs)
                else:
                    raise RuntimeError(f"Invalid skolem function: {name}")
        return Function(name, *targs)

class Statement:
    """Base class for all proof statements (Assumption, Axiom, Rule, Block)"""
    def __init__(self, ref: Ref = None, index: int = None, parent: 'Block' = None, formula: FirstOrderFormula = None):
        self.ref = ref
        self.index = index
        self.parent = parent
        self.formula = formula

    @staticmethod
    def replace_skolem_with_ref(formula_or_term):
        """
        Replace skolem constants from 'skolem_<id>' to 'skolem_<indices>' format.
        Example: 'skolem_5' where Ref.references[5].indices = (1, 2, 3)
                 becomes 'skolem_1_2_3'
        """
        return SkolemReplacer(formula_or_term).result

    @staticmethod
    def term_to_tptp(term: Term):
        return to_tptp_fof(Statement.replace_skolem_with_ref(term))

    @staticmethod
    def formula_to_tptp(formula: FirstOrderFormula):
        return to_tptp_fof(Statement.replace_skolem_with_ref(formula))

    def formula_of_statement_to_tptp(self):
        return Statement.formula_to_tptp(self.formula)

class Assumption(Statement):
    def __init__(
            self,
            formula: FirstOrderFormula,
            ref: Ref = None,
            index: int = None,
            parent: 'Block' = None,
    ):
        super().__init__(ref=ref, index=index, parent=parent, formula=formula)

    def to_ctxproof(self, depth: int = 0, ref: Ref = Ref([])):
        return f"{' ' * depth}{self.ref.to_ctxproof()} {self.formula_of_statement_to_tptp()} {{ASM}} {{{ref.to_ctxproof()}}};"

class Axiom(Statement):
    def __init__(
        self,
        label: str,
        fofs: list[FirstOrderFormula],
        terms: list[Term],
        formula: FirstOrderFormula,
        ref: Ref = None,
        index: int = None,
        parent: 'Block' = None,
    ):
        super().__init__(ref=ref, index=index, parent=parent, formula=formula)
        self.label = label
        self.fofs = fofs
        self.terms = terms

    def to_ctxproof(self, depth: int = 0):
        fofs_tptp = ';'.join(self.formula_to_tptp(f) for f in self.fofs)
        terms_tptp = ','.join(self.term_to_tptp(t) for t in self.terms)
        return (
            f"{' ' * depth}{self.ref.to_ctxproof()} {self.formula_of_statement_to_tptp()} {{A:{self.label}}} "
            f"{{{fofs_tptp}}} {{{terms_tptp}}};"
        )


class Rule(Statement):
    def __init__(
        self,
        label: str,
        refs: list[Ref],
        terms: list[Term],
        formula: FirstOrderFormula,
        ref: Ref = None,
        index: int = None,
        parent: 'Block' = None,
    ):
        super().__init__(ref=ref, index=index, parent=parent, formula=formula)
        self.label = label
        self.refs = refs
        self.terms = terms

    def transform_to_ctxproof(self, generic_formula):
        match generic_formula:
            case Ref():
                return generic_formula.to_ctxproof()
            case FirstOrderFormula():
                return self.formula_to_tptp(generic_formula)

        raise RuntimeError("Invalid formula")

    def to_ctxproof(self, depth: int = 0):
        return (
            f"{' ' * depth}{self.ref.to_ctxproof()} {self.formula_of_statement_to_tptp()} {{R:{self.label}}} "
            f"{{{';'.join(map(self.transform_to_ctxproof, self.refs))}}} {{{','.join(map(self.term_to_tptp, self.terms))}}};"
        )


class Block(Statement):
    def __init__(
        self,
        statements: list[Axiom | Rule | Self] = [],
        formula: FirstOrderFormula = None,
        ref: Ref = Ref([]),
        index: int = None,
        parent: 'Block' = None,
    ):
        super().__init__(ref=ref, index=index, parent=parent, formula=formula)
        self.statements = list(statements)
        self.ref_map = {}

    def get_formula(self):
        if self.statements:
            if type(self.statements[0]) is Assumption:
                return Implies(self.statements[0].formula, self.statements[-1].formula)
            else:
                return self.statements[-1].formula
        else:
            return None

    def value(self, ref : Ref):
        return ref.statement.formula

    def get_next_skolem_name(self):
        return f"skolem_{Ref.last_id + 1}"

    def get_depth(self):
        return len(self.ref.indices)

    def add(self, statement: Axiom | Rule | Self):
        statement.ref = Ref([])
        statement.ref.statement = statement
        statement.index = len(self.statements)
        statement.parent = self
        self.statements.append(statement)
        self.formula = self.get_formula()
        return statement

    def get_ctxproof_of_statement(self, statement, depth: int = 0):
        if type(statement) is Assumption:
            return statement.to_ctxproof(depth, ref=self.ref)
        else:
            return statement.to_ctxproof(depth)

    def to_ctxproof(self, depth: int = 0):
        if not self.statements:
            raise RuntimeError("Empty block")
        if type(self.statements[0]) is Assumption:
            res = f"{' ' * depth}{self.ref.to_ctxproof()} {self.formula_of_statement_to_tptp()}\n"
        else:
            res = f"{' ' * depth}{self.ref.to_ctxproof()} $true => {self.formula_of_statement_to_tptp()}\n"
        res += f"{' ' * depth}{{\n"
        for s in self.statements:
            res += self.get_ctxproof_of_statement(s, depth + 2) + "\n"
        res += f"{' ' * depth}}}"

        return res



PROOF : Block | None = None
CURRENT : Block | None = None
LANGUAGE: Language | None = None

def BEGIN(language: Language = None):
    Ref.last_id = 0
    global CURRENT, PROOF, LANGUAGE
    CURRENT = Block()
    PROOF = CURRENT
    LANGUAGE = language

class Context():
    def __enter__(self):
        global CURRENT, PROOF
        self.parent = CURRENT
        self.block = self.parent.add(Block())
        CURRENT = self.block
        return self.block

    def __exit__(self, exc_type, exc_val, exc_tb):
        global CURRENT
        self.block.formula = self.block.get_formula()
        self.parent.formula = self.parent.get_formula()
        CURRENT = self.parent
        return False

def ref():
    return reason.proofkit.kernel.proof.CURRENT.ref

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
    formula = reason.proofkit.kernel.Kernel.prove_tautology(PROOF)
    if type(PROOF.statements[0]) is Assumption:
        return formula
    else:
        match formula:
            case LogicConnective(name=IMP, args=[Predicate(name=const.TRUE), conclusion]):
                return conclusion

    raise RuntimeError("Invalid formula")

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

@asm
def PSU(r: Ref, predicate_pattern: Predicate, replacement: FirstOrderFormula):
    """
    p |- p(predicate_pattern/replacement)
    """
    formula_at_r = PROOF.value(r)
    result_formula = substitute_predicate(predicate_pattern, replacement, formula_at_r)

    return Rule("PSU", [r, predicate_pattern, replacement], [], result_formula)
