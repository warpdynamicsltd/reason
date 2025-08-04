from typing import Self

from reason.core.fof_types import *
from reason.core.transform.jsonize import jsonize

class Ref:
    def __init__(self, indices: list[int]):
        self.indices = indices

    def to_json(self) -> dict:
        # { "type": "Ref", "name": None, "args": [ index ] }
        return {"type": "Ref", "name": None, "args": self.indices}

class Assumption:
    def __init__(
            self,
            ref: Ref,
            formula: FirstOrderFormula,
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
        ref: Ref,
        label: str,
        fofs: list[FirstOrderFormula],
        terms: list[Term],
        formula: FirstOrderFormula,
    ):
        self.ref = ref
        self.label = label
        self.fofs = fofs
        self.terms = terms
        self.formula = formula

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
        ref: Ref,
        label: str,
        refs: list[Ref],
        terms: list[Term],
        formula: FirstOrderFormula,
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
        ref: Ref,
        statements: list[AxiomStmt | RuleStmt | Self],
        formula: FirstOrderFormula,
    ):
        self.ref = ref
        self.statements = statements
        self.formula = formula

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