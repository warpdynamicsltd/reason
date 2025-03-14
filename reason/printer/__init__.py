from collections import defaultdict

from reason.core import AbstractTerm
from reason.parser.tree import OperatorGrammarCreator
from reason.core.fof import *

class Printer:
    symb_mapping = {
        "NEG": "~",
        "AND": "∧",
        "OR": "∨",
        "IMP": "→",
        "IFF": "⟷",
        "FORALL": "∀",
        "EXISTS": "∃",
        "EQ": "=",
        "IN": "∈",
        "INCLUDES": "⊂",
        "INTERSECT": "∩",
        "UNION": "∪"
    }

    def __init__(self, ogc: OperatorGrammarCreator):
        self.ogc = ogc

        self.translate = defaultdict(list)

        for key, value in self.ogc.translate.items():
            self.translate[value].append(key)

        self.priority = {}
        for key in self.translate:
            for i, (_, _, sym_list) in enumerate(reversed(self.ogc.precedence)):
                if self.translate[key][0] in sym_list:
                    self.priority[key] = i

    def smart_bracket(self, parent_priority, priority, left_child, res):
        if parent_priority < priority:
            return f"{res}"
        else:
            if parent_priority == priority and left_child:
                return f"{res}"

            return f"({res})"

    def text(self, formula, parent_priority=-1, left_child=False):
        match formula:
            case LogicConnective(name=op, args=[a, b]):
                priority = self.priority[op]
                res = f"{self.text(a, priority, left_child=True)} {self.symb_mapping[op]} {self.text(b, priority)}"
                return self.smart_bracket(parent_priority, priority, left_child, res)

            case LogicConnective(name=op, args=[a]):
                priority = self.priority[op]
                res = f"{self.symb_mapping[op]}{self.text(a, priority, left_child=True)}"
                return self.smart_bracket(parent_priority, priority, left_child, res)

            case LogicQuantifier(name=op, args=[v, arg]):
                priority = self.priority[op]
                res = f"{self.symb_mapping[op]}{self.text(v)}. {self.text(arg, priority, left_child=True)}"
                return self.smart_bracket(parent_priority, priority, left_child, res)

            case Predicate(name=op, args=[a, b]) if op in {"EQ", "IN", "INCLUDES"}:
                priority = self.priority[op]
                res = f"{self.text(a, priority, left_child=True)} {self.symb_mapping[op]} {self.text(b, priority)}"
                return self.smart_bracket(parent_priority, priority, left_child, res)

            case Function(name=op, args=[a, b]) if op in {"UNION", "INTERSECT"}:
                priority = self.priority[op]
                res = f"{self.text(a, priority, left_child=True)} {self.symb_mapping[op]} {self.text(b, priority)}"
                return self.smart_bracket(parent_priority, priority, left_child, res)

            case AbstractTerm(name=name, args=args):
                if args:
                    return f"{name}({', '.join(map(self.text, args))})"
                else:
                    return f"{name}"

        return repr(formula)

    def __call__(self, formula):
        return self.text(formula)
