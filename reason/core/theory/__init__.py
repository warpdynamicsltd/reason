import sys
import subprocess

from enum  import Enum
from abc import ABC, abstractmethod
from typing import Iterator
from beartype import beartype


from reason.core.fof import *
from reason.core.theory.tautology import prove, Tautology
from reason.core.transform.base import remove_universal_quantifiers, quantifier_signature, free_variables
from reason.core.transform.describe import describe
from reason.core.language import Language, derive
from reason.core.transform.base import closure, prepend_quantifier_signature
from reason.parser.tree.consts import *

class AssertionStatus(Enum):
    null = 0
    computed_axiom = 1
    on_stack = 2
    proved = 3



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

    def declare_const(self, c: str):
        return self.get_langauge().add_const(c)

    def add_atomic_axiom(self, formula: FirstOrderFormula) -> FirstOrderFormula | None:
        if not self.is_on_stack(formula):
            return self._push(formula)

        return None

    def add_selection_axiom(self, formula: FirstOrderFormula) -> FirstOrderFormula | None:
        formula = remove_universal_quantifiers(formula)
        free_vars = free_variables(formula)
        res_formula = None
        match formula:
            case LogicQuantifier(name=const.EXISTS, args=[var, f]):
                if free_vars:
                    res_formula = f.replace(var, Function(self.get_langauge().get_unique_const_name(), *free_vars))
                else:
                    res_formula = f.replace(var, Const(name=self.get_langauge().get_unique_const_name()))

        if  res_formula is None:
            raise RuntimeError(f"unexpected formula {formula}")
        return self.add_atomic_axiom(res_formula)



    def is_consts_declaration_with_constrain(self, formula: FirstOrderFormula, consts: list[Const]) -> bool:
        formula = closure(formula)

        test_formula = formula

        q_signature = []
        for c in consts:
            if not self.is_used(Const, c):
                var = Variable(c)
                test_formula = test_formula.replace(Const(c), var)
                q_signature.append((EXISTS, var))


        if not q_signature:
            return False

        test_formula = prepend_quantifier_signature(test_formula, q_signature)

        _, status = self.add_formula(test_formula)
        if status != AssertionStatus.null:
            return True

        return False

    def is_term_definition(self, formula: FirstOrderFormula) -> bool:
        formula = remove_universal_quantifiers(formula)
        match formula:
            case LogicConnective(name=const.IMP, args=[definition, condition]):
                definition_variables = free_variables(definition)
                condition_variables = free_variables(condition)
                if condition_variables.issubset(definition_variables):
                    match definition:
                        case Predicate(name=const.EQ, args=[f, y]):
                            if (type(y) is Variable and
                                type(f) is Function and
                                not self.is_used(Function, f.name)):

                                condition_variables.remove(y)
                                test_formula = condition
                                signature = [(FORALL, v) for v in condition_variables] + [(EXISTS, y)]
                                test_formula = prepend_quantifier_signature(test_formula, signature)
                                _, status = self.add_formula(test_formula)
                                if status != AssertionStatus.null:
                                    return True

        return False



    def is_definition_axiom(self, formula: FirstOrderFormula) -> bool:
        formula = remove_universal_quantifiers(formula)
        variables = free_variables(formula)
        match formula:
            case LogicConnective(name=const.IFF, args=[a, b]):
                description = describe(b)
                match a:
                    case Predicate(name=name):
                        if free_variables(a) != variables:
                            return False
                        if name not in description[Predicate] and not self.is_used(Predicate, name):
                            return True

            case Predicate(name=const.EQ, args=[a, b]):
                description = describe(b)
                match a:
                    case Function(name=name):
                        if free_variables(a) != variables:
                            return False
                        if name not in description[Function] and not self.is_used(Function, name):
                            return True

        if self.is_term_definition(formula):
            return True

        return False

    @beartype
    def is_axiom(self, formula: FirstOrderFormula) -> AssertionStatus:
        if self.is_computed_axiom(formula):
            return AssertionStatus.computed_axiom

        return AssertionStatus.null

    def is_provable(self, formula: FirstOrderFormula) -> AssertionStatus:
        if self.is_on_stack(formula):
            return AssertionStatus.on_stack

        status = self.is_axiom(formula)
        if status != AssertionStatus.null:
            return status

        premises = self.get_stack_iter()
        try:
            proof = prove(formula, premises=premises)
        except subprocess.CalledProcessError as e:
            print(f"can't prove {self.L.printer(closure(formula))}")
            sys.exit(1)

        if proof is not None:
            self.store(formula, proof)
            return AssertionStatus.proved

        return AssertionStatus.null

    def add_definition(self, formula: FirstOrderFormula) -> FirstOrderFormula:
        formula = closure(formula)
        if self.is_definition_axiom(formula):
            formula = self._push(formula)
            return formula

        raise RuntimeError(f"formula {formula} is not a definition axiom")

    @beartype
    def declare_consts_with_constrain(self, formula: FirstOrderFormula, consts: list[str]) -> FirstOrderFormula:
        formula = closure(formula)
        if self.is_consts_declaration_with_constrain(formula, consts):
            formula = self._push(formula)
            return formula

        raise RuntimeError("formula is not a definition axiom")

    @beartype
    def add_formula(self, formula: FirstOrderFormula) -> tuple[FirstOrderFormula, AssertionStatus]:
        status = self.is_provable(formula)
        if status == AssertionStatus.on_stack:
            return formula, status
        elif status != AssertionStatus.null:
            formula = self._push(formula)
            return formula, status
        else:
            raise RuntimeError("formula not provable")


def overwritten(x):
    return x
