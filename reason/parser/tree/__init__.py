import re
from lark import Transformer, v_args, Token

from reason.parser.utils import v_args_return_with_meta
from reason.core import AbstractTerm
from reason.parser.tree.consts import *


class AbstractSyntaxTree(AbstractTerm):
    def flat_to_tree(self, target_name, left_join=True):
        if len(self.args) == 1:
            return self.args[0]

        if len(self.args) < 2:
            raise ValueError("Too few args")

        args = self.args
        if left_join is False:
            args = list(reversed(self.args))
            obj = AbstractSyntaxTree(target_name, args[1], args[0])
        else:
            obj = AbstractSyntaxTree(target_name, args[0], args[1])

        for arg in args[2:]:
            if left_join:
                obj = AbstractSyntaxTree(target_name, obj, arg)
            else:
                obj = AbstractSyntaxTree(target_name, arg, obj)

        return obj


class OperatorGrammarCreator:
    precedence = [
        ("std", 2, ["∩"]),
        ("std", 2, ["∪"]),
        ("std", 2, ["∈", "=", "⊂"]),
        ("std", 3, {(":", "↦"): MAPS}),
        ("std", 1, ["~"]),
        ("std", 2, ["and", "∧"]),
        ("std", 2, ["or", "∨"]),
        ("std", 2, ["→", "⇒", "⟷", "⇔"]),
        ("quantifier", 1, ["∀", "∃"]),
    ]

    translate = {
        "~": NEG,
        "and": AND,
        "∧": AND,
        "or": OR,
        "∨": OR,
        "→": IMP,
        "⇒": IMP,
        "⟷": IFF,
        "⇔": IFF,
        "∀": FORALL,
        "∃": EXISTS,
        "∈": IN,
        "=": EQ,
        "∩": INTERSECT,
        "∪": UNION,
        "⊂": INCLUDES,
    }

    def __init__(self, super_rule, main_rule, prefix):
        self.super_rule = super_rule
        self.main_rule = main_rule
        self.prefix = prefix
        self.longer_ops = {}

    def create_terminal_rule(self, level, arity, terms):
        return f"OP{arity}_{level}.1: {'| '.join(map(lambda s: chr(34) + s + chr(34), terms))}\n"

    def create_terminals(self):
        res = str()
        for i, (t, arity, terms) in enumerate(self.precedence):
            level = i + 1
            if arity <= 2:
                res += self.create_terminal_rule(level, arity, terms)

        return res

    def create_rule(self, level, arity):
        match arity:
            case 1:
                return f"{self.prefix}_{level}: OP{arity}_{level} {self.prefix}_{level} -> _op{arity} | {self.prefix}_{level - 1}\n"
            case 2:
                return f"{self.prefix}_{level}: {self.prefix}_{level} OP{arity}_{level} {self.prefix}_{level - 1} -> _op{arity} | {self.prefix}_{level - 1}\n"

        raise RuntimeError(f"Unknown arity: {arity}")

    def create_longer_operator_rule(self, level, term):
        rule = f"{self.prefix}_{level}: "
        for i, key in enumerate(term):
            name = term[key]
            rule += f"{self.prefix}_{level}"
            for c in key:
                rule += f' "{c}" {self.prefix}_{level}'

            rule += f" -> op_{name.lower()}"
            rule += " | "
        rule += f"{self.prefix}_{level - 1}\n"

        return rule


    def create_longer_operator_rules(self):
        rule = f"{self.main_rule}_longer_op: "
        for i, key in enumerate(self.longer_ops):
            name = self.longer_ops[key]
            rule += f"{self.main_rule}"
            for c in key:
                rule += f' "{c}" {self.main_rule}'

            rule += f" -> op_{name.lower()}"

            if i < len(self.longer_ops) - 1:
                rule += " | "

        return rule

    def create_quantifier_rule(self, level):
        return f'{self.prefix}_{level}: OP1_{level} "(" abstract_term_list ")" {self.prefix}_{level} -> _op_quant | OP1_{level} abstract_term_list "." {self.prefix}_{level} -> _op_quant | {self.prefix}_{level - 1}\n'

    def create_rules(self):
        res = str()
        for i, (t, arity, terms) in enumerate(self.precedence):
            level = i + 1
            if arity <= 2:
                match t:
                    case "std":
                        res += self.create_rule(level, arity)
                    case "quantifier":
                        res += self.create_quantifier_rule(level)
            else:
                res += self.create_longer_operator_rule(level, terms)


        return res

    def create_bracket_rule(self):
        return f'{self.prefix}_0: {self.super_rule} | "(" {self.main_rule} ")" -> bracket\n'

    def create_main_rule(self):
        return f"{self.main_rule}: {self.prefix}_{len(self.precedence)}\n"

    def create_lark_code(self):
        res = "\n\n"
        res += self.create_main_rule() + "\n"
        res += self.create_bracket_rule() + "\n"
        res += self.create_terminals() + "\n"
        res += self.create_rules() + "\n"
        # res += self.create_longer_operator_rules() + "\n"

        return res


class ReasonTreeToAbstractSyntaxTree(Transformer):
    abstract_term_list = list
    abstract_term_list_spec = list

    def __init__(self, level_prefix, *args, **kwargs):
        self.level_prefix = level_prefix
        Transformer.__init__(self, *args, **kwargs)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def symbol(self, symbol):
        return symbol.value

    # @v_args(inline=True)
    @v_args_return_with_meta
    def atom_term(self, symbol):
        return AbstractSyntaxTree(symbol)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def fname(self, symbol):
        return symbol

    # @v_args(inline=True)
    @v_args_return_with_meta
    def composed_abstract_term(self, fname, term_list):
        return AbstractSyntaxTree(fname, *term_list)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def abstract_term_sequence(self, abstract_term_list_spec):
        return AbstractSyntaxTree(f"{SEQ}{len(abstract_term_list_spec)}", *abstract_term_list_spec)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def abstract_term_set(self, abstract_term_list):
        # (s,) = s
        return AbstractSyntaxTree(f"{SET}{len(abstract_term_list)}", *abstract_term_list)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def abstract_term_selection(self, logic_simple1, logic_simple2):
        return AbstractSyntaxTree(SELECT, logic_simple1, logic_simple2)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def _op1(self, op, arg):
        op = OperatorGrammarCreator.translate[op]
        return AbstractSyntaxTree(op, arg)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def _op2(self, abstract_term1, op, abstract_term2):
        op = OperatorGrammarCreator.translate[op]
        return AbstractSyntaxTree(op, abstract_term1, abstract_term2)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def _op_quant(self, op, abstract_term_list, abstract_term):
        op = OperatorGrammarCreator.translate[op]
        res = AbstractSyntaxTree(op, abstract_term_list[-1], abstract_term)
        for v in reversed(abstract_term_list[:-1]):
            res = AbstractSyntaxTree(op, v, res)

        return res

    @v_args_return_with_meta
    def op_maps(self, agr1, arg2, arg3):
        return AbstractSyntaxTree("MAPS", agr1, arg2, arg3)

    # @v_args(inline=True)
    @v_args_return_with_meta
    def logic_simple(self, logic_simple):
        return logic_simple

    # @v_args(inline=True)
    @v_args_return_with_meta
    def bracket(self, term):
        return term

    # @v_args(inline=True)
    @v_args_return_with_meta
    def abstract_term(self, abstract_term):
        return abstract_term

    @staticmethod
    def prefix_rule_handler(s):
        return s

    def __default__(self, data, children, meta):
        match data:
            case Token(type="RULE", value=value) if re.match(f"^{self.level_prefix}_\\d+$", value):
                (s,) = children
                res = self.prefix_rule_handler(s)
                if isinstance(res, AbstractSyntaxTree):
                    setattr(res, "meta", meta)
                return res

        raise RuntimeError(f"Unexpected RULE {data}")
