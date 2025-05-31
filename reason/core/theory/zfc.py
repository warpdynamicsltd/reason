from typing import List, Sequence
from abc import ABC, abstractmethod
import logging

from reason.core.theory import BaseTheory, overwritten
from reason.core.language import Language
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
        
        self.description = {
            Const: set(),
            Function: set(),
            Predicate: set()
        }

        self._add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)")
        self._add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))")
        self._add_axiom("empty(∅)")
        self._add_axiom("∀(x, z) z ∈ {x} ⟷ z = x")
        self._add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y")
        self._add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y")
        self._add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)")
        self._add_axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)")
        # self._add_axiom("{a, b} = {a} ∪ {b}")
        # self._add_axiom("(a, b) = {a, {a, b}}")

    @overwritten
    def _push(self, formula: FirstOrderFormula):
        formula = closure(formula)
        self.formulas_stack.append(formula)
        self.stack_signatures.add(formula_sha256(formula))
        self.update_description(formula)

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
    def is_atomic_axiom(self, formula: FirstOrderFormula) -> bool:
        hash = formula_sha256(formula)
        return hash in self.simple_axioms_signatures
    
    @overwritten
    def is_computed_axiom(self, formula):
        return False
    
    @overwritten
    def is_used(self, t, name):
        return name in self.description[t]

    
    def update_description(self, formula):
        description = describe(formula)
        for key in self.description:
            self.description[key] |= description[key]

    def _add_const(self, c: str):
        self.L.add_const(c)

    def _add_axiom(self, s: str):
        formula = self.L(s)
        self.simple_axioms_signatures.add(formula_sha256(formula))

    def add(self, s: str):
        formula = self.L(s)
        self.add_formula(formula)
        logging.info("added %s", self.L.printer(formula))
        
