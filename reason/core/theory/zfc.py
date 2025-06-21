from typing import List, Sequence
from abc import ABC, abstractmethod
from collections import Counter
import logging

from reason.core.theory import BaseTheory, overwritten
from reason.core.language import Language, derive
from reason.core.fof_types import *
from reason.core.transform.signature import formula_sha256
from reason.core.transform.base import closure
from reason.core.transform.describe import describe


class ZFC(BaseTheory):
    def __init__(self):
        self.L = Language()

        self._add_const("∅")

        self.simple_axioms_signatures = set()
        self.formulas_stack = []
        self.stack_signatures = set()
        self.proofs = {}

        self.description = {Const: Counter(), Function: Counter(), Predicate: Counter()}

    @overwritten
    def _push(self, formula: FirstOrderFormula) -> FirstOrderFormula:
        formula = closure(formula)
        self.formulas_stack.append(formula)
        self.stack_signatures.add(formula_sha256(formula))
        self.update_description(formula)
        return formula

    @overwritten
    def _pop(self) -> FirstOrderFormula:
        formula = self.formulas_stack.pop()
        self.stack_signatures.remove(formula_sha256(formula))
        self.update_description(formula, removes=True)
        return formula

    @overwritten
    def store(self, formula: FirstOrderFormula, proof: dict):
        hash = formula_sha256(formula)
        self.proofs[hash] = proof

    @overwritten
    def is_on_stack(self, formula: FirstOrderFormula) -> bool:
        hash = formula_sha256(formula)
        return hash in self.stack_signatures

    @overwritten
    def get_stack_iter(self) -> Sequence[FirstOrderFormula]:
        return iter(self.formulas_stack)

    @overwritten
    def get_stack_len(self) -> int:
        return len(self.formulas_stack)

    @overwritten
    def is_computed_axiom(self, formula):
        return False

    @overwritten
    def is_used(self, t: type, name: str):
        return name in self.description[t] and self.description[t][name] > 0

    @overwritten
    def get_langauge(self):
        return self.L

    def update_description(self, formula, removes=False):
        description = describe(formula)
        if not removes:
            for key in self.description:
                for item in description[key]:
                    self.description[key][item] += 1
        else:
            for key in self.description:
                for item in description[key]:
                    self.description[key][item] -= 1

    def _add_const(self, c: str):
        self.L.add_const(c)

    def axiom(self, s: str):
        formula = self.L(s)
        self.add_atomic_axiom(formula)

    def add(self, s: str):
        formula = self.L(s)
        self.add_formula(formula)
