from functools import cache
from reason.core import AbstractTerm

class GrammarTerm(AbstractTerm):
    pass

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

    # @cache
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


def main():
    d = digit()
    e = end()

    number = GrammarNode("number")
    start = GrammarNode("start")
    sum = GrammarNode("sum")
    exp = GrammarNode("exp")

    number == d | d + number
    exp == number | st("(") + sum + st(")")
    sum == exp | exp + st("+") + sum
    start == sum + e

    print(list(start("1223")))

if __name__ == "__main__":
    main()


