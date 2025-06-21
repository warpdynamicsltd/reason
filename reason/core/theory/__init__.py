from enum  import Enum
from abc import ABC, abstractmethod
from typing import List, Generator, Iterator
from beartype import beartype

from reason.core.fof import *
from reason.core.theory.tautology import prove, Tautology
from reason.core.transform.base import remove_universal_quantifiers
from reason.core.transform.describe import describe
from reason.core.language import Language, derive
from reason.parser.tree.consts import *

class AssertionStatus(Enum):
    null = 0
    computed_axiom = 1
    definition = 2
    on_stack = 3
    proved = 4



class BaseTheory(ABC):
    @abstractmethod
    def store(self, formula: FirstOrderFormula, proof: dict):
        pass

    @abstractmethod
    def is_on_stack(self, formula: FirstOrderFormula) -> bool:
        pass

    @abstractmethod
    def _push(self, formula: FirstOrderFormula):
        pass

    @abstractmethod
    def _pop(self) -> FirstOrderFormula:
        pass

    @abstractmethod
    def get_stack_iter(self) -> Iterator[FirstOrderFormula]:
        pass

    @abstractmethod
    def get_stack_len(self) -> int:
        pass

    @abstractmethod
    def is_computed_axiom(self, formula: FirstOrderFormula) -> bool:
        pass

    @abstractmethod
    def is_used(self, t: type, name: str) -> bool:
        pass

    @abstractmethod
    def get_langauge(self) -> Language:
        pass

    def derive_language(self) -> Language:
        return derive(self.get_langauge())

    def formula(self, ast: AbstractSyntaxTree):
        return self.get_langauge().to_formula(ast)

    def add_atomic_axiom(self, formula: FirstOrderFormula) -> FirstOrderFormula | None:
        if not self.is_on_stack(formula):
            return self._push(formula)

        return None

    def is_definition_axiom(self, formula: FirstOrderFormula) -> bool:
        formula = remove_universal_quantifiers(formula)
        match formula:
            case LogicConnective(name=const.IFF, args=[a, b]):
                description = describe(b)
                match a:
                    case Predicate(name=name):
                        if name not in description[Predicate] and not self.is_used(Predicate, name):
                            return True

            case Predicate(name=const.EQ, args=[a, b]):
                description = describe(b)
                match a:
                    case Const(name=name):
                        if name not in description[Const] and not self.is_used(Const, name):
                            return True

                    case Function(name=name):
                        if name not in description[Function] and not self.is_used(Function, name):
                            return True

        return False

    @beartype
    def is_axiom(self, formula: FirstOrderFormula) -> AssertionStatus:
        if self.is_computed_axiom(formula):
            return AssertionStatus.computed_axiom

        if self.is_definition_axiom(formula):
            return AssertionStatus.definition

        return AssertionStatus.null

    def is_provable(self, formula: FirstOrderFormula) -> AssertionStatus:
        if self.is_on_stack(formula):
            return AssertionStatus.on_stack

        status = self.is_axiom(formula)
        if status != AssertionStatus.null:
            return status

        premises = self.get_stack_iter()
        proof = prove(formula, premises=premises)
        if proof is not None:
            self.store(formula, proof)
            return AssertionStatus.proved

        return AssertionStatus.null

    def add_formula(self, formula: FirstOrderFormula) -> tuple[FirstOrderFormula | None, AssertionStatus]:
        status = self.is_provable(formula)
        if status == AssertionStatus.on_stack:
            return None, status
        elif status != AssertionStatus.null:
            formula = self._push(formula)
            return formula, status
        else:
            raise RuntimeError("formula not provable")


def overwritten(x):
    return x
