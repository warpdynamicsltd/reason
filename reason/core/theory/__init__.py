from abc import ABC, abstractmethod
from typing import List, Generator, Iterator
from reason.core.fof import *
from reason.core.theory.tautology import prove, Tautology
from reason.core.transform.base import remove_universal_quantifiers
from reason.core.transform.describe import describe
from reason.parser.tree.consts import *

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
    def get_stack_iter(self) -> Iterator[FirstOrderFormula]:
        pass
    
    @abstractmethod
    def is_atomic_axiom(self, formula: FirstOrderFormula) -> bool:
        pass

    @abstractmethod
    def is_computed_axiom(self, formula: FirstOrderFormula) -> bool:
        pass

    @abstractmethod
    def is_used(self, t, name):
        pass

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


    def is_axiom(self, formula: FirstOrderFormula) -> bool:
        if self.is_atomic_axiom(formula):
            return True
        
        if self.is_computed_axiom(formula):
            return True
        
        if self.is_definition_axiom(formula):
            return True
        
        return False


    def is_provable(self, formula: FirstOrderFormula) -> bool:
        if self.is_axiom(formula):
            return True
        
        if self.is_on_stack(formula):
            return True
        
        premises = self.get_stack_iter()
        proof = prove(formula, premises=premises)
        if proof is not None:
            self.store(formula, proof)
            return True
        
        return False
    
    def add_formula(self, formula: FirstOrderFormula):
        if self.is_provable(formula):
            self._push(formula)
        else:
            raise RuntimeError("formula not provable")


def overwritten(x):
    return x 
        

