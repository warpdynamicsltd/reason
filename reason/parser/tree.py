from lark import Transformer
from reason.core import AbstractTerm

class OperatorGrammarCreator:
  precedence = [
    (2, ['∈', '=']),
    (1, ['~']),
    (2, ['and']),
    (2, ['or']),
    (2, ['→', '⇒', '⟷', '⇔']),
  ]

  translate = {
    '~': 'NEG',
    'and': 'AND',
    '∧': 'AND',
    'or': 'OR',
    '∨': 'OR',
    '→': 'IMP',
    '⇒': 'IMP',
    '⟷': 'IFF',
    '⇔': 'IFF',
    '∀': 'FORALL',
    '∃': 'EXISTS',
    '∈': 'IN',
    '=': 'EQ'
  }

  def __init__(self, super_rule, main_rule, prefix):
    self.super_rule = super_rule
    self.main_rule = main_rule
    self.prefix = prefix

  def create_terminal_rule(self, level, arity, terms):
    return f"OP{arity}_{level}: {'| '.join(map(lambda s: chr(34) + s + chr(34), terms))}\n"
  
  def create_terminals(self):
    res = str()
    for i, (arity, terms) in enumerate(self.precedence):
      level = i + 1
      res += self.create_terminal_rule(level, arity, terms)

    return res
  
  def create_rule(self, level, arity):
    res = str()
    if arity == 2:
      res = f"{self.prefix}_{level}: {self.prefix}_{level} OP{arity}_{level} {self.prefix}_{level - 1} -> _op{arity} | {self.prefix}_{level - 1}\n"
    else:
      res = f"{self.prefix}_{level}: OP{arity}_{level} {self.prefix}_{level - 1} -> _op{arity} | {self.prefix}_{level - 1}\n"
    
    return res
  
  def create_rules(self):
    res = str()
    for i, (arity, terms) in enumerate(self.precedence):
      level = i + 1
      res += self.create_rule(level, arity)

    return res
  
  def create_bracket_rule(self):
    return f'{self.prefix}_0: {self.super_rule} | "(" {self.main_rule} ")" -> brk\n'
  
  def create_main_rule(self):
    return f"{self.main_rule}: {self.prefix}_{len(self.precedence)}\n"

  def create_lark_code(self):
    res = "\n\n"
    res += self.create_main_rule() + '\n'
    res += self.create_bracket_rule() + '\n'
    res += self.create_terminals() + '\n'
    res += self.create_rules() + '\n'

    return res

class TreeToAbstractTerm(Transformer):
  def atom_term(self, s):
    (s,) = s
    return AbstractTerm(s)
  
  def brk(self, s):
    (s,) = s
    return s
  
  def fname(self, s):
    (s,) = s
    return s
  
  def abstract_term_list(self, terms):
    return list(terms)
  
  def composed_abstract_term(self, s):
    fname, term_list = s
    return AbstractTerm(fname, *term_list)
  
  def neg(self, s):
    (op, s) = s
    return AbstractTerm("NEG", s)
  
  def _or(self, s):
    a, op, b = s
    return AbstractTerm("OR", a, b)
  
  def _and(self, s):
    a, op, b = s
    return AbstractTerm("AND", a, b)
  
  def _impl(self, s):
    a, op, b = s
    return AbstractTerm("IMP", a, b)
  
  def _op1(self, s):
    op, a = s
    op = OperatorGrammarCreator.translate[op]
    return AbstractTerm(op, a)
  
  def _op2(self, s):
    a, op, b = s
    # print(a, op, b, type(op))
    op = OperatorGrammarCreator.translate[op]
    return AbstractTerm(op, a, b)
  
  def __default__(self, data, children, meta):
    # print(children)
    if not children:
      return None
    (s,) = children
    return s