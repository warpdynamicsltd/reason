from reason.parser.tree import *
from reason.core import AbstractTerm, Variable, Const

def to_fof(obj):
  match obj:
    case AbstractTerm(name='NEG', args=[a]):
      return f"(~{to_fof(a)})"
    
    case AbstractTerm(name='AND', args=[a, b]):
      return f"({to_fof(a)} & {to_fof(b)})"
    
    case AbstractTerm(name='OR', args=[a, b]):
      return f"({to_fof(a)} | {to_fof(b)})"
    
    case AbstractTerm(name='IMP', args=[a, b]):
      return f"({to_fof(a)} => {to_fof(b)})"
    
    case AbstractTerm(name='IFF', args=[a, b]):
      return f"({to_fof(a)} <=> {to_fof(b)})"
    
    case AbstractTerm(name='FORALL', args=[x, a]):
      return f"(![{to_fof(x)}] : ({to_fof(a)}))"
    
    case AbstractTerm(name='EXISTS', args=[x, a]):
      return f"(?[{to_fof(x)}] : ({to_fof(a)}))"
    
    case AbstractTerm(name='CONJUNCTION', args=args):
      return f"({' & '.join(map(to_fof, args))})"
    
    case Variable(name=f, args=[]):
      return f"V_{f}"
    
    case Const(name=c, args=[]):
      return f"c_{c}"
    
    case AbstractTerm(name=f, args=args):
      return f"f_{f}({','.join(map(to_fof, args))})"
    
  return obj
