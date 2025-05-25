from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory_v1 import Theory_v1

reason_parser = Parser()
vampire_prover = Vampire()

ZFC = Theory_v1(parser=reason_parser, prover=vampire_prover)

ZFC.add_const("∅")

ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
ZFC.add_axiom("empty(∅)", name="a1")
ZFC.add_axiom("∀(x, z) z ∈ {x} ⟷ z = x", name="a3")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name="a4")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name="a5")
ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name="d2")

premise = "~({x} ∩ {y} = ∅)"
thesis = "x = y"

proof = """{
  ~({x} ∩ {y} = ∅);
  ∃(z){
    z ∈ {x} ∧ z ∈ {y};
    z = x ∧ z = y;
    ∀(k) ((k ∈ x ⟷ k ∈ z) ∧ (k ∈ z ⟷ k ∈ y));
    x = y;
    };
}
"""

print(ZFC.check_proof(premise, thesis, proof))

# True
