from reason.core import AbstractTerm, Variable, Const

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

  def add_formula(self, text, name, type):
    s = self.parser(text)
    s = self.rectify(s)
    self.axioms.append(s)
    # print(s)
    self.prover.add_formula(s, name, type)

  def add_axiom(self, text, name):
    s = self.parser(text)
    s = self.rectify(s)
    self.axioms.append(s)
    # print(s)
    self.prover.add_axiom(s, name)

  def __call__(self, text):
    s = self.parser(text)
    s = self.rectify(s)
    return self.prover(s)

