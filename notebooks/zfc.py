#%%
import json
import sys
import json

from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory
from reason.core.transform.skolem import skolem_sha256
from reason.core.transform.signature import formula_sha256, signature

reason_parser = Parser()
vampire_prover = Vampire()

ZFC = Theory(parser=reason_parser, prover=vampire_prover, cache_folder_path=None)

ZFC.add_const("∅")

ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
ZFC.add_axiom("empty(∅)", name="a1")
ZFC.add_axiom("∀(x, z) z ∈ {x} ⟷ z = x", name="a3")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name="a4")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name="a5")
ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name="d2")
ZFC.add_axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)", name="a6")
ZFC.add_axiom("{a, b} = {a} ∪ {b}", name="d3")
ZFC.add_axiom("(a, b) = {a, {a, b}}", name="d4")

ZFC.add_axiom("(a, b, c) = ((a, b), c)", name="d5")

ZFC.absorb_cache()

#%%
ZFC.prove("{x ∈ a: P(x)} ∪ {x ∈ a: Q(x)} ⊂ {x ∈ a: P(x) ∨ Q(x)}")

#%%
proof_obj = ZFC.prove("∃p. p = {x ∈ a: P(x)}")
if proof_obj is not None:
  print("OK")

#%%
proof_obj = ZFC.prove("{x ∈ a: P(x)} ⊂ a")
if proof_obj is not None:
  print("OK")

#%%
proof_obj = ZFC.prove("(k ∈ a ∧ P(k)) ∨ (k ∈ a ∧ Q(k)) ⟷ k ∈ a ∧ (P(k) ∨ Q(k))")
if proof_obj is not None:
  print("OK")

#%%
premise = None
thesis = "{x ∈ a: P(x)} ∪ {x ∈ a: Q(x)} ⊂ {x ∈ a: P(x) ∨ Q(x)}"

proof = """
{
  ∃p. { 
    p = {x ∈ a: P(x)};
    ∃q. {
          q = {x ∈ a: Q(x)};
          (∀ k. k ∈ p ∪ q ⟷ k ∈ p ∨ k ∈ q);
          (∀ k. k ∈ p ∨ k ∈ q ⟷ (k ∈ a ∧ P(k)) ∨ (k ∈ a ∧ Q(k)));
          (∀ k. (k ∈ a ∧ P(k)) ∨ (k ∈ a ∧ Q(k)) ⟷ k ∈ a ∧ (P(k) ∨ Q(k)));
          (∀ k. k ∈ a ∧ (P(k) ∨ Q(k)) ⟷ k ∈ {x ∈ a: P(x) ∨ Q(x)});
    };
    p ∪ q ⊂ {x ∈ a: P(x) ∨ Q(x)};
  };
}
"""

print(ZFC.check_proof(premise, thesis, proof))

#%%
obj = ZFC.prove("(a, b) = (c, d) → a = c ∧ b = d")
print(obj)

obj = ZFC.prove("(a, b) = (c, d) → a = c ∧ b = d")
print(obj)


#%%

obj = ZFC.prove("(a, b, c) = (x, x, x) → a = b")
print(obj)

#%%

obj = ZFC.prove("(a, b, c) = (x, y, z) → a = x ∧ b = y ∧ c = z")
print(obj)


#%%
f = ZFC.compile("(a, b) = (c, d) → a = c ∧ b = d")
# print(ZFC.prover.run(f, output_axiom_names="on"))
obj = ZFC.prove(f)
print(obj)
#print(json.dumps(obj, indent=2))



#%%
f = ZFC.compile("a ∪ b = b ∪ a")
# print(ZFC.prover.run(f, output_axiom_names="on"))
obj = ZFC.prove(f)
print(obj)
#print(json.dumps(obj, indent=2))

#%%
f_a4 = ZFC.tptp_parser("(![V_x1] : ((![V_x2] : ((![V_x3] : ((p_IN(V_x3,f_UNION(V_x1,V_x2)) <=> (p_IN(V_x3,V_x1) | p_IN(V_x3,V_x2)))))))))")
print(formula_sha256(f_a4))
print(signature(f_a4))
print(signature(ZFC.compile("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y")))


#f = ZFC.compile("(a, b) = (c, d) → a = c ∧ b = d")
# print(ZFC.prover.run(f, output_axiom_names="on"))

# proof = ZFC.prove(f)
# if proof is not None:
#     json.dump(proof, sys.stdout, indent=2)

#%%
f = ZFC.compile("(a, b) = (c, d) → b = d ∧ c = a")
print(skolem_sha256(f))

#%%
T = Theory(parser=reason_parser, prover=vampire_prover)
#T.add_const("∅")


#%%
T("(a, b) = (c, d) → a = c ∧ b = d")



#%%
premise = "(a, b, c) = (x, x, x)"
thesis = "a = b"

proof = """{
    (a, b, c) = (x, x, x);
    ∃(z) {
      z = (a, b, c);
      z = ((a, b), c);
      z = (x, x, x);
      z = ((x, x), x);
      ((a, b), c) = ((x, x), x);
      (a, b) = (x, x);
      a = x ∧ b = x;
      a = b}
    }
"""

# proof = """{
#     (a, b, c) = (x, x, x);
#     ((a, b), c) = ((x, x), x);
#     ((a, b), c) = ((x, x), x) → (a, b) = (x, x) ∧ c = x;
#     (a, b) = (x, x);
#     (a, b) = (x, x) → a = x ∧ b = x;
#     a = x ∧ b = x;
#     a = b;
# }
# """

print(ZFC.check_proof(premise, thesis, proof))

#%%
ZFC("(a, b, c) = ((a, b), c)")