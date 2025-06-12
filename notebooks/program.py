#%%
import logging

from reason.parser import ProgramParser
from reason.core.theory.zfc import ZFC
from reason.core.interpreter import Interpreter

logging.basicConfig(level=logging.INFO)


program_parser = ProgramParser()

code = \
"""
    ∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y);
    empty(e) ⟷ (∀(x) ~(x ∈ e));
    empty(∅);
    ∀(x, z) z ∈ {x} ⟷ z = x;
    ∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y;
    ∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y;
    ∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y);
    ∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅);
    
    begin
        take a, b, c, p, q;
        assume p = a ∩ (b ∪ c);
        assume q = (a ∩ b) ∪ (a ∩ c);
        then p = q; 
    end;
    
    a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c);
"""

program_ast = program_parser(code)
interpreter = Interpreter(ZFC())

interpreter(program_ast)