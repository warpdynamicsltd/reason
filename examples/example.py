from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory

reason_parser = Parser()
vampire_prover = Vampire()

ZFC = Theory(parser=reason_parser, prover=vampire_prover)

ZFC.add_const("∅")

ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
ZFC.add_axiom("empty(∅)", name="a1")
ZFC.add_axiom("∀(x, z) z ∈ s(x) ⟷ z = x", name="a3")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name='a4')
ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name='a5')
ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name='d2')

print(ZFC("∀(x) empty(x) → x = ∅"))
print(ZFC("∀(x, y) s(x) = s(y) → x = y"))
print(ZFC("∀(x, y) x ∩ y ⊂ x ∪ y"))

# True
# True
# True