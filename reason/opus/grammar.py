class GrammarNode:
    @staticmethod
    def factory(func):
        def wrapper(*args, **kwargs):
            def f(s, index):
                yield from func(s, index, *args, **kwargs)
            t = GrammarNode()
            t.call = f
            return t

        return wrapper

    def call(self, s, index):
        yield index

    def __call__(self, s, index=0):
        yield from self.call(s, index)

    def __add__(self, other):
        def f(s, index):
            for i in self(s, index):
                for j in other(s, i):
                    yield j

        t = type(self)()
        t.call = f
        return t

    def __or__(self, other):
        def f(s, index):
            for i in self(s, index):
                yield i
            for i in other(s, index):
                yield i

        t = type(self)()
        t.call = f
        return t

    def __eq__(self, other):
        self.call = other.call

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


