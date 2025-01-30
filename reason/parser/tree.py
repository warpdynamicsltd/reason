from lark import Transformer
from reason.core import AbstractTerm

NEG = 'NEG'
AND = 'AND'
OR = 'OR'
IMP = 'IMP'
IFF = 'IFF'
FORALL = 'FORALL'
EXISTS = 'EXISTS'
IN = 'IN'
EQ = 'EQ'

class OperatorGrammarCreator:
  precedence = [
    ('std', 2, ['∩']),
    ('std', 2, ['∪']),
    ('std', 2, ['∈', '=', '⊂']),
    ('std', 1, ['~']),
    ('std', 2, ['and', '∧']),
    ('std', 2, ['or', '∨']),
    ('std', 2, ['→', '⇒', '⟷', '⇔']),
    ('quantifier', 1, ['∀', '∃'])
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
    '=': 'EQ',
    '∩': 'INTERSECT',
    '∪': 'UNION',
    '⊂': 'INCLUDES'
  }

  def __init__(self, super_rule, main_rule, prefix):
    self.super_rule = super_rule
    self.main_rule = main_rule
    self.prefix = prefix

  def create_terminal_rule(self, level, arity, terms):
    return f"OP{arity}_{level}.1: {'| '.join(map(lambda s: chr(34) + s + chr(34), terms))}\n"
  
  def create_terminals(self):
    res = str()
    for i, (t, arity, terms) in enumerate(self.precedence):
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
  
  def create_quantifier_rule(self, level):
    return f"{self.prefix}_{level}: OP1_{level} \"(\" abstract_term_list \")\" {self.prefix}_{level} -> _op_quant | {self.prefix}_{level - 1}\n"

  
  def create_rules(self):
    res = str()
    for i, (t, arity, terms) in enumerate(self.precedence):
      level = i + 1
      match t:
        case 'std':
          res += self.create_rule(level, arity)
        case 'quantifier':
          res += self.create_quantifier_rule(level)



    return res
  
  def create_bracket_rule(self):
    return f'{self.prefix}_0: {self.super_rule} | "(" {self.main_rule} ")" -> brk | "{{" {self.main_rule}_list "}}" -> conj_formula \n'
  
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
    # print(type(s), s)
    return AbstractTerm(s)
  
  def brk(self, s):
    (s,) = s
    return s
  
  def fname(self, s):
    (s,) = s
    return s
  
  def abstract_term_list(self, terms):
    return list(terms)
  
  def abstract_term_list_spec(self, terms):
    return list(terms)
  
  def conj_formula(self, s):
    (s, ) = s
    return AbstractTerm('CONJUNCTION', *s)

  def logic_simple_list(self, terms):
    return list(terms)
  
  def composed_abstract_term(self, s):
    fname, term_list = s
    return AbstractTerm(fname, *term_list)
  
  def abstract_term_sequence(self, s):
    (s,) = s
    return AbstractTerm(f"SEQ{len(s)}", *s)
  
  def abstract_term_set(self, s):
    (s,) = s
    return AbstractTerm(f"SET{len(s)}", *s)
  
  # def neg(self, s):
  #   (op, s) = s
  #   return AbstractTerm("NEG", s)
  
  # def _or(self, s):
  #   a, op, b = s
  #   return AbstractTerm("OR", a, b)
  
  # def _and(self, s):
  #   a, op, b = s
  #   return AbstractTerm("AND", a, b)
  
  # def _impl(self, s):
  #   a, op, b = s
  #   return AbstractTerm("IMP", a, b)
  
  def _op1(self, s):
    op, a = s
    op = OperatorGrammarCreator.translate[op]
    return AbstractTerm(op, a)
  
  def _op2(self, s):
    a, op, b = s
    # print(a, op, b, type(op))
    op = OperatorGrammarCreator.translate[op]
    return AbstractTerm(op, a, b)
  
  def _op_quant(self, s):
    op, l, a = s
    op = OperatorGrammarCreator.translate[op]
    res = AbstractTerm(op, l[-1], a)
    for v in reversed(l[:-1]):
      res = AbstractTerm(op, v, res)

    return res

  
  def __default__(self, data, children, meta):
    # print(children)
    if not children:
      return None
    (s,) = children
    return s