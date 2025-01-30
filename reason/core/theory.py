from reason.core import AbstractTerm, Variable, Const
from reason.core.transform import explode_over_conjunctions

class Theory:
  def __init__(self, parser, prover):
    self.parser = parser
    self.prover = prover
    self.axioms = []
    self.consts = {}

  def rectify(self, s):
    match s:
      case AbstractTerm(name=x, args=[]):
        # print('type:', type(x), 'value:', x)
        if x in self.consts:
          # print('>>>', x)
          return Const(name=self.consts[x])
        else:
          return Variable(name=x)
      
    return AbstractTerm(s.name, *list(map(self.rectify, s.args)))

  def add_const(self, c):
    self.consts[c] = f"c{len(self.consts)}"

  def add_formula(self, f: str | AbstractTerm, name, type):
    s = self.symbolise(f)
    s = self.rectify(s)
    self.axioms.append(s)
    # print(s)
    self.prover.add_formula(s, name, type)

  def add_axiom(self, f: str | AbstractTerm, name):
    s = self.symbolise(f)
    s = self.rectify(s)
    self.axioms.append(s)
    # print(s)
    self.prover.add_axiom(s, name)

  def __call__(self, f: str | AbstractTerm):
    if not isinstance(f, AbstractTerm):
      s = self.parser(f)
    else:
      s = f
    s = self.rectify(s)
    return self.prover(s)
  
  
  def symbolise(self, f):
    if not isinstance(f, AbstractTerm):
      return self.parser(f)
    else:
      return f
  

  def check_proof(self, premise: str | AbstractTerm, thesis: str | AbstractTerm, proof: str | AbstractTerm):
    premise = self.symbolise(premise)
    thesis = self.symbolise(thesis)
    proof = self.symbolise(proof)

    consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
    return all(self(AbstractTerm('IMP', source, target)) for source, target in zip(consequences[:-1], consequences[1:]))
  
  def add_lemmas(self, premise: str | AbstractTerm, thesis: str | AbstractTerm, proof: str | AbstractTerm):
    premise = self.symbolise(premise)
    thesis = self.symbolise(thesis)
    proof = self.symbolise(proof)

    if self.check_proof(premise, thesis, proof):
      consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
      for source, target in zip(consequences[:-1], consequences[1:]):
        formula=AbstractTerm('IMP', source, target)
        self.add_formula(formula, name=f"lemma{id(formula)}", type="theorem")
      return True
    
    return False


