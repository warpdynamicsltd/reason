from beartype import beartype

# from reason.parser.tree import *
from reason.core.fof_types import LogicPredicate
from reason.core.fof_types import Const, FirstOrderFormula, Function, Predicate, Variable
from reason.tools.math.transform import utf8_to_varname, varname_to_utf8


def name_tptp_encode(s: str):
    return utf8_to_varname(s)


def name_tptp_decode(s: str):
    return varname_to_utf8(s)


def to_tptp_fof(obj: FirstOrderFormula) -> str:
    """
    Converts FirstOrderFormula object to fof string from TPTP language for use in Vampire
    """
    match obj:
        case LogicPredicate(name="NEG", args=[a]):
            return f"(~{to_tptp_fof(a)})"

        case LogicPredicate(name="AND", args=[a, b]):
            return f"({to_tptp_fof(a)} & {to_tptp_fof(b)})"

        case LogicPredicate(name="OR", args=[a, b]):
            return f"({to_tptp_fof(a)} | {to_tptp_fof(b)})"

        case LogicPredicate(name="IMP", args=[a, b]):
            return f"({to_tptp_fof(a)} => {to_tptp_fof(b)})"

        case LogicPredicate(name="IFF", args=[a, b]):
            return f"({to_tptp_fof(a)} <=> {to_tptp_fof(b)})"

        case LogicPredicate(name="FORALL", args=[x, a]):
            return f"(![{to_tptp_fof(x)}] : ({to_tptp_fof(a)}))"

        case LogicPredicate(name="EXISTS", args=[x, a]):
            return f"(?[{to_tptp_fof(x)}] : ({to_tptp_fof(a)}))"

        # case FirstOrderFormula(name='CONJUNCTION', args=args):
        #   return f"({' & '.join(map(to_fof, args))})"

        case Predicate(name="EQ", args=[a, b]):
            return f"({to_tptp_fof(a)}={to_tptp_fof(b)})"

        case Variable(name=f, args=[]):
            return f"V_{f}"

        case Const(name=c, args=[]):
            return f"c_{name_tptp_encode(c)}"

        case Predicate(name=f, args=[]):
            return f"p_{f}"

        case Predicate(name=f, args=args):
            return f"p_{f}({','.join(map(to_tptp_fof, args))})"

        case Function(name=f, args=args):
            return f"f_{f}({','.join(map(to_tptp_fof, args))})"

    return obj
