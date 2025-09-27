from functools import cache
from typing import Callable
from reason.parser import AbstractSyntaxTree
from reason.opus.transformer import GrammarTerm, Transformer


class GrammarNode:
    @staticmethod
    def factory(func):
        def wrapper(*args, **kwargs):
            def f(s, index):
                for i in func(s, index, *args, **kwargs):
                    yield i, GrammarTerm(func.__name__, s[index:i])
            t = GrammarNode(func.__name__)
            t.call = f
            return t

        return wrapper

    def __init__(self, name=None, consumable=True):
        self.name = name
        self.consumable = consumable

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        id(self) == id(other)

    def call(self, s, index):
        yield index

    @cache
    def __call__(self, s, index=0):
        return tuple(self.call(s, index))

    @staticmethod
    def _to_grammar_list(obj, node):
        if obj.consumable:
            lst = [node]
        else:
            lst = []
        return GrammarTerm("_list", *lst)

    def add_grammar_node(self, other):
        def f(s, index):
            for i, n in self(s, index):
                if n.name != "_list":
                    n = self._to_grammar_list(self, n)
                for j, m in other(s, i):
                    if m.name != "_list":
                        m = self._to_grammar_list(other, m)
                    yield j, GrammarTerm("_list", *n.args, *m.args)

        t = type(self)("_list")
        t.call = f
        return t

    def add_str(self, s: str):
        other = st(s)
        other.consumable = False
        return self.add_grammar_node(other)

    def radd_str(self, s: str):
        other = st(s)
        other.consumable = False
        return other.add_grammar_node(self)

    def __add__(self, other):
        match other:
            case GrammarNode():
                return self.add_grammar_node(other)
            case str():
                return self.add_str(other)

        raise RuntimeError("Invalid grammar node")

    def __radd__(self, other):
        match other:
            case str():
                return self.radd_str(other)

        raise RuntimeError("Invalid grammar node")


    def __or__(self, other):
        def f(s, index):
            for i, n in self(s, index):
                yield i, n
            for i, n in other(s, index):
                yield i, n

        t = type(self)()
        t.call = f
        return t

    def __eq__(self, other):
        def f(s, index):
            for i, n in other(s, index):
                yield i, GrammarTerm(self.name, n)
        self.call = f

    def rshift_str(self, name: str):
        res = type(self)(name=name)
        res == self
        return res

    def rshift_func(self, transform: Callable):
        res = self.rshift_str(transform.__name__)
        setattr(res, "transform", transform)
        return res

    def __rshift__(self, arg):
        match arg:
            case str():
                return self.rshift_str(arg)
            case func if isinstance(func, Callable):
                return self.rshift_func(func)

        raise RuntimeError("Invalid grammar node")



def repeat(gn: GrammarNode):
    def f(s, index):
        first_res = list(gn(s, index))
        if not first_res:
            yield index, GrammarTerm("_list")
        for i, n in first_res:
            if n.name != "_list":
                n = GrammarTerm("_list", n)
            for j, m in f(s, i):
                yield j, GrammarTerm("_list", *n.args, *m.args)

    res_gn = GrammarNode("_list")
    res_gn.call = f
    return res_gn >> f"repeat_{gn.name}"

@GrammarNode.factory
def digit(s, index):
    if index < len(s) and s[index].isdigit():
        yield index + 1

@GrammarNode.factory
def st(s, index, c: str):
    if index < len(s) and s[index:index + len(c)] == c:
        yield index + len(c)

@GrammarNode.factory
def end(s, index):
    if index >= len(s):
        yield index


class AddingTransformer(Transformer):
    @Transformer.vargs
    def number(self, *digits):
        return int("".join(digits))

    @Transformer.vargs
    def bracket(self, n):
        return n

    @Transformer.vargs
    def repeat_direct_sum(self, *args):
        if args:
            ast = AbstractSyntaxTree("ADD", *[n for (n,) in args])
            return ast.flat_to_tree("ADD")

    @Transformer.vargs
    def sum(self, *arg):
        s, n = arg
        if s:
            return AbstractSyntaxTree("ADD", s, n)
        else:
            return n

    @Transformer.vargs
    def start(self, value, e):
        return value

@Transformer.vargs
def bracket(n):
    return n



def main():
    d = digit()
    e = end()

    number = GrammarNode("number")
    start = GrammarNode("start")
    sum = GrammarNode("sum")
    exp = GrammarNode("exp")

    number == d | d + number >> "composed_number"
    exp == number | "(" + sum + ")" >> "bracket"
    sum == exp | exp + "+" + sum >> "direct_sum"
    start == sum + e

    [(i, node)] = start("1+2+3")
    print(i)
    print(node)
    print(AddingTransformer().transform(node))

def main2():
    d = digit()
    e = end()

    number = GrammarNode("number")
    start = GrammarNode("start")
    sum = GrammarNode("sum")
    exp = GrammarNode("exp")

    number == repeat(d)
    exp == number | "(" + sum + ")" >> bracket
    sum == repeat(exp + "+" >> "direct_sum") + exp
    start == sum + e

    [(i, node)] = start("1+2+3")
    print(i)
    print(node)
    print(AddingTransformer().transform(node))

if __name__ == "__main__":
    main2()


