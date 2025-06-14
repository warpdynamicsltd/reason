#%%
import importlib
from reason.core import AbstractTerm, AbstractTermMutable
from reason.parser.tree import AbstractSyntaxTree
from reason.core.transform import explode_over_conjunctions
from reason.vampire.translator import to_tptp_fof
from reason.parser import Parser

#%%
importlib.reload(reason)

parser = Parser()
#%%
gt = parser("{p; q; r; s}")
#%%
gt
#%%
gt.flat_to_tree('AND', left_join=True)
#%%
a  = AbstractTermMutable.immutable_copy(AbstractTermMutable('A', AbstractTermMutable('B')), AbstractTerm)
#%%
type(a.args)
#%%
type("int")
#%%
import logging
import sys

# Configure the logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to standard output
    ]
)
#%%
print(parser.ogc.create_lark_code())
#%%
formula = parser("y = {x, a, b}")
#%%
formula._args
#%%
formula.args
#%%
from reason.core.theory_v1 import Theory_v1
from reason.vampire import Vampire
vampire_prover = Vampire(verbose=True)
ZFC = Theory_v1(parser, vampire_prover)

ZFC.add_const("∅")

ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
ZFC.add_axiom("empty(∅)", name="a1")
ZFC.add_axiom(r"∀(x, z) z ∈ {x} ⟷ z = x", name="a3")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name='a4')
ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name='a5')
ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name='d2')
ZFC.add_axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)", name='a6')
ZFC.add_axiom(r"{a, b} = {a} ∪ {b}", name='d3')
ZFC.add_axiom(r"(a, b) = {a, {a, b}}", name='d3')

# ZFC.add_formula("∀(z) z ∈ a ∩ (b ∪ c) → z ∈ (a ∩ b) ∪ (a ∩ c)", name='t1', type="theorem")
# ZFC.add_formula("∀(z) z ∈ (a ∩ b) ∪ (a ∩ c) → z ∈ a ∩ (b ∪ c)", name='t2', type="theorem")

# ZFC.add_formula("(x = z ∧ z = y) → ((((∀(k) k ∈ x ⟷ k ∈ z) ∧ (∀(k) k ∈ z ⟷ k ∈ y) → (∀(k) (k ∈ x ⟷ k ∈ y)))) → (x = y))", 
#                 name="t3",
#                 type="theorem")

# ZFC.add_formula("~(s(x) ∩ s(y) = ∅) → (∃(z) z ∈ s(x) ∧ z ∈ s(y) ∧ z = x ∧ z = y)", 
#                 name="t4",
#                 type="theorem")
#%%
ZFC(r"{a, b} = {c} → a = b")
#%%
ZFC("{a, b} = {b, a}")
#%%
ZFC("(a, b) = (c, d) → a = c ∧ b = d")
#%%
premise = "s(a) ∪ s(s(a) ∪ s(b)) = s(c) ∪ s(s(d)) "
thesis = "a = c ∧ b = d"

proof = """
  {
    s(a) ∪ s(s(b)) = s(c) ∪ s(s(d));
    a ∈ s(c) ∨ a ∈ s(s(d));
    a ∈ s(c) → a = c;
    a ∈ s(s(d)) → 
      {
        a = s(d);
        
      }
  }
"""

print(ZFC.check_proof(premise, thesis, proof))
#%%
premise = "s(x) = s(y)"
thesis =  "s(x) = s(y)"

proof = """
    {x = y;
    ∀(z) z ∈ x ⟷ z ∈ y;
    ∀(v) v ∈ s(x) ⟷ v = x;
    ∀(v) v ∈ s(y) ⟷ v = y;
    ∀(v) v ∈ s(y) ⟷ v ∈ s(x);
    s(x) = s(y);}
"""

print(ZFC.check_proof(premise, thesis, proof))
#%%
ZFC("~(s(x) ∩ s(y) = ∅) → x = y")
#%%
premise = "~(s(x) ∩ s(y) = ∅)"
thesis = "x = y"

proof = """{
  ~(s(x) ∩ s(y) = ∅);
  ∃(z){
    z ∈ s(x) ∧ z ∈ s(y);
    z = x ∧ z = y;
    ∀(k) (k ∈ x ⟷ k ∈ z) ∧ (k ∈ z ⟷ k ∈ y);
    x = y;
    };

}
"""

print(ZFC.check_proof(premise, thesis, proof))
#%%
ZFC.add_lemmas(premise, thesis, proof)
#%%

#%%
from reason.vampire.translator import to_tptp_fof
#%%
premise = parser("~(s(x) ∩ s(y) = ∅)")
thesis = parser("x = y")
theorem = AbstractTerm('IMP', premise, thesis)
#%%
#theorem = parser("∀(x, y) ~(s(x) ∩ s(y) = ∅) → x = y") 
#%%
proof = """{
  ~(s(x) ∩ s(y) = ∅);
  ∃(z){
    z ∈ s(x) ∧ z ∈ s(y);
    z = x ∧ z = y;
    ∀(k) (k ∈ x ⟷ k ∈ z) ∧ (∀(k) k ∈ z ⟷ k ∈ y);
    x = y
    }
}
"""

proof_formula = parser(proof)
#%%
consequences = [premise] + explode_over_conjunctions(proof_formula) + [thesis]
all(ZFC(AbstractTerm('IMP', source, target)) for source, target in zip(consequences[:-1], consequences[1:]))
#%%

#%%
formulas
#%%
imp = AbstractTerm('IMP', proof_formula, theorem)
ZFC(imp)
#%%

#%%
ZFC("~(x ∈ y) ∧ (x ∈ y)")
#%%
ZFC("~(s(x) ∩ s(y) = ∅) → x = y")
#%%
ZFC("""(∀(x, y, z, k)
~(s(x) ∩ s(y) = ∅) and
z ∈ s(x) ∧ z ∈ s(y) and
z = x ∧ z = y and
(k ∈ z ⟷ k ∈ x) ∧ (k ∈ z ⟷ k ∈ y) and
(k ∈ x ⟷ k ∈ y) and
x = y        
) → ( ∀(x, y) ~(s(x) ∩ s(y) = ∅) → x = y )""")
#%%
ZFC("""(
~(s(x) ∩ s(y) = ∅) and
z ∈ s(x) ∧ z ∈ s(y) and
z = x ∧ z = y and
(k ∈ z ⟷ k ∈ x) ∧ (k ∈ z ⟷ k ∈ y) and
(k ∈ x ⟷ k ∈ y) and
x = y        
) → ( ~(s(x) ∩ s(y) = ∅) → x = y )""")
#%%
ZFC(
  """
  (~(s(x) ∩ s(y) = ∅)) → ((∃(z) (z ∈ s(x) ∧ z ∈ s(y)) → (∃(z) ∀(k) (k ∈ z ⟷ k ∈ x) ∧ (k ∈ z ⟷ k ∈ y))))
  """
)
#%%
ZFC("""(~(s(x) ∩ s(y) = ∅)) → (
~(s(x) ∩ s(y) = ∅) and
(∃(z) (z ∈ s(x) ∧ z ∈ s(y) and
z = x ∧ z = y and
(∀(k)((k ∈ z ⟷ k ∈ x) ∧ (k ∈ z ⟷ k ∈ y) and
(k ∈ x ⟷ k ∈ y) and
x = y        
)))))""")
#%%
ZFC("s(x) = s(y) → x = y")
#%%
ZFC("a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)")
#%%
ZFC("∀(x, y) empty(x) ∧ empty(y) → x = y")
#%%
ZFC("empty(x) → x = ∅")
#%%
ZFC("s(x) = s(y) → x = y")
#%%
ZFC("∀(x, y, z) z = s(x) ∪ s(y) → x ∈ z ∧ y ∈ z")
#%%
ZFC("~(s(x) ∩ s(y) = ∅) → (∃(z) z ∈ s(x) ∧ z ∈ s(y) ∧ z = x ∧ z = y)")
#%%
ZFC("(z = x ∧ z = y) → x = y")
#%%
ZFC("~(s(x) ∩ s(y) = ∅) → x = y")
#%%
ZFC("~(s(x) ∩ s(y) = ∅) → (∃(z) z ∈ s(x) ∧ z ∈ s(y))")
#%%
ZFC("∀(x, y, z) z ∈ s(x) ∧ z ∈ s(y) → z = x ∧ z = y")
#%%
ZFC("∀(x, y, z) x = z ∧ z = y → x = y")
#%%
ZFC("(x = z ∧ z = y) → ((((∀(k) k ∈ x ⟷ k ∈ z) ∧ (∀(k) k ∈ z ⟷ k ∈ y) → (∀(k) (k ∈ x ⟷ k ∈ y)))) → x = y)")