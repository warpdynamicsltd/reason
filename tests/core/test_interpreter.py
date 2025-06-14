import unittest

from reason.parser import ProgramParser
from reason.core.theory.zfc import ZFC
from reason.core.interpreter import Interpreter

class TestZFCTheory(unittest.TestCase):
    def test_interpreter_zfc_basic(self):
        program_parser = ProgramParser()

        code = \
            """
                assume ∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y);
                assume empty(e) ⟷ (∀(x) ~(x ∈ e));
                assume empty(∅);
                assume ∀(x, z) z ∈ {x} ⟷ z = x;
                assume ∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y;
                assume ∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y;
                assume ∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y);
                assume ∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅);
    
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