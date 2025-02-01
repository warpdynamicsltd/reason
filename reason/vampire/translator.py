from beartype import beartype

# from reason.parser.tree import *
from reason.core import Variable, Const
from reason.core.fof import FirstOrderFormula


def to_fof(obj: FirstOrderFormula) -> str:
  """
  Converts FirstOrderFormula object to fof string from TPTP language for use in Vampire
  """
  match obj:
    case FirstOrderFormula(name='NEG', args=[a]):
      return f"(~{to_fof(a)})"
    
    case FirstOrderFormula(name='AND', args=[a, b]):
      return f"({to_fof(a)} & {to_fof(b)})"
    
    case FirstOrderFormula(name='OR', args=[a, b]):
      return f"({to_fof(a)} | {to_fof(b)})"
    
    case FirstOrderFormula(name='IMP', args=[a, b]):
      return f"({to_fof(a)} => {to_fof(b)})"
    
    case FirstOrderFormula(name='IFF', args=[a, b]):
      return f"({to_fof(a)} <=> {to_fof(b)})"
    
    case FirstOrderFormula(name='FORALL', args=[x, a]):
      return f"(![{to_fof(x)}] : ({to_fof(a)}))"
    
    case FirstOrderFormula(name='EXISTS', args=[x, a]):
      return f"(?[{to_fof(x)}] : ({to_fof(a)}))"
    
    # case FirstOrderFormula(name='CONJUNCTION', args=args):
    #   return f"({' & '.join(map(to_fof, args))})"
    
    case FirstOrderFormula(name='EQ', args=[a, b]):
      return f"({to_fof(a)}={to_fof(b)})"
    
    case Variable(name=f, args=[]):
      return f"V_{f}"
    
    case Const(name=c, args=[]):
      return f"c_{c}"
    
    case FirstOrderFormula(name=f, args=args):
      return f"f_{f}({','.join(map(to_fof, args))})"
    
  return obj
