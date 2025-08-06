from typing import Self

from reason.core.fof_types import *
from reason.core.fof_ops import *
from reason.core.transform.jsonize import jsonize

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

class AxiomStmt:
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

class RuleStmt:
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


class BlockStmt:
    def __init__(
        self,
        statements: list[AxiomStmt | RuleStmt | Self] = [],
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
        if type(statement) is BlockStmt:
            if len(ref.indices) > 1:
                ref = Ref(list(ref.indices)[1:])
                return statement.value(ref)
            else:
                return statement.formula
        else:
            return statement.formula

    def get_next_ref(self):
        return Ref(list(self.ref.indices) + [len(self.statements)])

    def add(self, statement: AxiomStmt | RuleStmt | Self):
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