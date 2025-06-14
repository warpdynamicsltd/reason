import unittest

from reason.parser import ProgramParser
from reason.core.theory.zfc import ZFC
from reason.core.interpreter import Interpreter

class TestZFCTheory(unittest.TestCase):
    codes = [
        """
        assume ∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y);
        assume empty(e) ⟷ (∀(x) ~(x ∈ e));
        assume empty(∅);
        assume ∀(x, z) z ∈ {x} ⟷ z = x;
        assume ∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y;
        assume ∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y;
        assume ∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y);
        assume ∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅);
        
        assume {a, b} = {a} ∪ {b};
        assume (a, b) = {a, {a, b}};
        
        begin
            take a, b;
            assume a ∈ b;
            assume b ∈ a;
        
            take e;
            assume e = {a, b};
            ~(a ∩ e = ∅);
            b ∩ e = ∅;
            then ~(a ∈ b);
        end;
        ~(a ∈ b ∧ b ∈ a);
        """,
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
    ]
    def test_interpreter_zfc_basic(self):
        program_parser = ProgramParser()

        for code in self.codes:
            program_ast = program_parser(code)
            interpreter = Interpreter(ZFC())

            interpreter(program_ast)