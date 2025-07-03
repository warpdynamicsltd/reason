import unittest

from importlib.resources import files
from reason.core.theory.zfc import ZFC
from reason.interpreter import Interpreter


class TestZFCTheory(unittest.TestCase):
    codes = [
        """
        use ∅;
        axiom ∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y);
        axiom empty(e) ⟷ (∀(x) ~(x ∈ e));
        axiom empty(∅);
        axiom ∀(x, z) z ∈ {x} ⟷ z = x;
        axiom ∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y;
        axiom ∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y;
        axiom ∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y);
        axiom ∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅);
        
        let {a, b} = {a} ∪ {b};
        let (a, b) = {a, {a, b}};
        
        begin
            take a, b;
            assume a ∈ b;
            assume b ∈ a;
        
            pick e where e = {a, b};
            ~(a ∩ e = ∅);
            b ∩ e = ∅;
            then ~(a ∈ b);
        end;
        ~(a ∈ b ∧ b ∈ a);
        """,
        """
        use ∅;
        axiom ∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y);
        axiom empty(e) ⟷ (∀(x) ~(x ∈ e));
        axiom empty(∅);
        axiom ∀(x, z) z ∈ {x} ⟷ z = x;
        axiom ∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y;
        axiom ∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y;
        axiom ∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y);
        axiom ∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅);

        begin
            take a, b, c;
            pick p where p = a ∩ (b ∪ c);
            pick q where q = (a ∩ b) ∪ (a ∩ c);
            p = q;
            then a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c);
        end;

        a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c);
        """
    ]
    def test_interpreter_zfc_basic(self):
        for code in self.codes:
            interpreter = Interpreter(ZFC())

            interpreter.run_code(code)

    def test_interpreter_zfc_files(self):
        filenames = [
            "examples/basic/hello.rsn",
            "examples/basic/hello2.rsn",
            "examples/basic/tuples.rsn",
            "examples/basic/example.rsn",
            "examples/basic/example2.rsn",
            "examples/basic/sum.rsn",
            "examples/basic/int.rsn",
            "examples/basic/ind.rsn",
            "examples/basic/fun_def.rsn",
            "examples/basic/prod.rsn",
            "theories/ZFC/zfc.rsn"

        ]
        root_examples = files("reason") / ".."


        for filename in filenames:
            filename = root_examples / filename
            interpreter = Interpreter(ZFC())
            interpreter.run_file(str(filename))

