from abc import ABC, abstractmethod
from typing import List, Generator, Iterator
from reason.core.fof import FirstOrderFormula
from reason.core.theory.tautology import prove, Tautology

class BaseTheory:
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
    def is_axiom(self, formula: FirstOrderFormula) -> bool:
        pass

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
        

