from beartype import beartype

from reason.core import AbstractTerm, Variable, Const
from reason.core.fof import FirstOrderFormula
from reason.parser.tree import GrammarTree
from reason.core.transform import explode_over_conjunctions

class Theory:
  def __init__(self, parser, prover):
    self.parser = parser
    self.prover = prover
    self.axioms = []
    self.consts = {}

  @staticmethod
  def unflatten_conjunctions(g : GrammarTree) -> GrammarTree:
    match g:
      case GrammarTree(name='CONJUNCTION'):
        return g.flat_to_tree('AND')
      
    return g

  @beartype
  def to_formula(self, s : GrammarTree) -> Const | Variable | FirstOrderFormula:
    s = self.unflatten_conjunctions(s)
    match s:
      case GrammarTree(name=x, args=[]):
        if x in self.consts:
          return Const(name=self.consts[x])
        else:
          return Variable(name=x)

    return FirstOrderFormula(s.name, *map(self.to_formula, s.args))

  def add_const(self, c : str):
    self.consts[c] = f"c{len(self.consts)}"

  @beartype
  def add_formula(self, f: str | GrammarTree, name, type):
    s = self.symbolise(f)
    s = self.to_formula(s)
    self.axioms.append(s)
    # print(s)
    self.prover.add_formula(s, name, type)

  @beartype
  def add_axiom(self, f: str | GrammarTree, name):
    s = self.symbolise(f)
    s = self.to_formula(s)
    self.axioms.append(s)
    # print(s)
    self.prover.add_axiom(s, name)

  @beartype
  def __call__(self, f: str | GrammarTree) -> bool:
    s = self.symbolise(f)
    s = self.to_formula(s)
    return self.prover(s)
  
  @beartype
  def symbolise(self, f: str | GrammarTree) -> GrammarTree:
    if not isinstance(f, GrammarTree):
      return self.parser(f)
    else:
      return f
  
  @beartype
  def check_proof(self, premise: str | GrammarTree, thesis: str | GrammarTree, proof: str | GrammarTree) -> bool:
    premise = self.symbolise(premise)
    thesis = self.symbolise(thesis)
    proof = self.symbolise(proof)

    consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
    return all(self(GrammarTree('IMP', source, target)) for source, target in zip(consequences[:-1], consequences[1:]))
  
  @beartype
  def add_lemmas(self, premise: str | GrammarTree, thesis: str | GrammarTree, proof: str | GrammarTree) -> bool:
    premise = self.symbolise(premise)
    thesis = self.symbolise(thesis)
    proof = self.symbolise(proof)

    if self.check_proof(premise, thesis, proof):
      consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
      for source, target in zip(consequences[:-1], consequences[1:]):
        formula=GrammarTree('IMP', source, target)
        self.add_formula(formula, name=f"lemma{id(formula)}", type="theorem")
      return True
    
    return False


