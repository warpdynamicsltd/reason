from lark import Transformer
from reason.core import AbstractTerm

class GrammarTree(AbstractTerm):
  
  def flat_to_tree(self, target_name, left_join=True):
    if len(self.args) == 1:
      return self.args[0]
    
    if len(self.args) < 2:
      raise ValueError("Too few args")
    
    args = self.args
    if left_join is False:
      args = list(reversed(self.args))
      obj = GrammarTree(target_name, args[1], args[0])
    else:
      obj = GrammarTree(target_name, args[0], args[1])

    for arg in args[2:]:
      if left_join:
        obj = GrammarTree(target_name, obj, arg)
      else:
        obj = GrammarTree(target_name, arg, obj)

    return obj



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

class TreeToGrammarTree(Transformer):
  def atom_term(self, s):
    (s,) = s
    # print(type(s), s)
    return GrammarTree(s)
  
  # def brk(self, s):
  #   (s,) = s
  #   return s
  
  # def fname(self, s):
  #   (s,) = s
  #   return s
  
  def abstract_term_list(self, terms):
    return list(terms)
  
  def abstract_term_list_spec(self, terms):
    return list(terms)
  
  def conj_formula(self, s):
    (s, ) = s
    return GrammarTree('CONJUNCTION', *s)

  def logic_simple_list(self, terms):
    return list(terms)
  
  def composed_abstract_term(self, s):
    fname, term_list = s
    return GrammarTree(fname, *term_list)
  
  def abstract_term_sequence(self, s):
    (s,) = s
    return GrammarTree(f"SEQ{len(s)}", *s)
  
  def abstract_term_set(self, s):
    (s,) = s
    return GrammarTree(f"SET{len(s)}", *s)
  
  
  def _op1(self, s):
    op, a = s
    op = OperatorGrammarCreator.translate[op]
    return GrammarTree(op, a)
  
  def _op2(self, s):
    a, op, b = s
    # print(a, op, b, type(op))
    op = OperatorGrammarCreator.translate[op]
    return GrammarTree(op, a, b)
  
  def _op_quant(self, s):
    op, l, a = s
    op = OperatorGrammarCreator.translate[op]
    res = GrammarTree(op, l[-1], a)
    for v in reversed(l[:-1]):
      res = GrammarTree(op, v, res)

    return res

  
  def __default__(self, data, children, meta):
    # print(children)
    if not children:
      return None
    (s,) = children
    return s