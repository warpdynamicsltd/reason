from functools import cache
from reason.parser import AbstractSyntaxTree
from reason.opus.transformer import GrammarTerm, Transformer


class GrammarNode:
    @staticmethod
    def factory(func):
        def wrapper(*args, **kwargs):
            def f(s, index):
                for i in func(s, index, *args, **kwargs):
                    yield i, GrammarTerm(func.__name__, s[index:i])
            t = GrammarNode()
            t.call = f
            return t

        return wrapper

    def __init__(self, name=None):
        self.name = name

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        id(self) == id(other)

    def call(self, s, index):
        yield index

    @cache
    def __call__(self, s, index=0):
        return tuple(self.call(s, index))

    def __add__(self, other):
        def f(s, index):
            for i, n in self(s, index):
                if type(n) is not list:
                    n = [n]
                for j, m in other(s, i):
                    if type(m) is not list:
                        m = [m]
                    yield j, n + m

        t = type(self)()
        t.call = f
        return t

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
                if type(n) is list:
                    yield i, GrammarTerm(self.name, *n)
                else:
                    yield i, GrammarTerm(self.name, n)
        self.call = f

    def __rshift__(self, name: str):
        res = type(self)(name=name)
        res == self
        return res

def repeat(gn: GrammarNode):
    def f(s, index):
        first_res = list(gn(s, index))
        if not first_res:
            yield index, []
        for i, n in first_res:
            for j, m in f(s, i):
                if type(m) is not list:
                    m = [m]
                yield j, [n] + m

    return f

    res_gn = GrammarNode()
    res_gn.call = f
    return res_gn


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
    def digit(self, n):
        return n

    def end(self, e):
        return e

    def st(self, c):
        return c

    def composed_number(self, d, n):
        return d + n

    def number(self, n):
        return n

    def bracket(self, lb, value, rb):
        return value

    def direct_sum(self, value, op, sum):
        return AbstractSyntaxTree(op, value, sum)

    def exp(self, value):
        return value

    def sum(self, value):
        return value

    def start(self, value, e):
        return value




def main():
    d = digit()
    e = end()

    number = GrammarNode("number")
    start = GrammarNode("start")
    sum = GrammarNode("sum")
    exp = GrammarNode("exp")

    number == d | d + number >> "composed_number"
    exp == number | st("(") + sum + st(")") >> "bracket"
    sum == exp | exp + st("+") + sum >> "direct_sum"
    start == sum + e

    [(i, node)] = start("(1+2)+(3+41)")
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
    exp == number | st("(") + sum + st(")") >> "bracket"
    sum == exp + repeat(st("+") + exp >> "direct_sum")
    start == sum + e

    [(i, node)] = start("1+2+3+4")
    print(i)
    print(node)

if __name__ == "__main__":
    main2()


