class GrammarNode:
    def call(self, s, index):
        yield index

    def __call__(self, s, index):
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

    def __le__(self, other):

        self.call = other.call


def digit():
    def f(s, index):
        if index < len(s) and s[index].isdigit():
            yield index + 1

    t = GrammarNode()
    t.call = f
    return t

def char(c: str):
    def f(s, index):
        if index < len(s) and s[index] == c:
            yield index + 1

    t = GrammarNode()
    t.call = f
    return t

def end():
    def f(s, index):
        if index >= len(s):
            yield index

    t = GrammarNode()
    t.call = f
    return t


def satisfy(s):
    d = digit()
    number = GrammarNode()
    start = GrammarNode()
    sum = GrammarNode()
    exp = GrammarNode()
    e = end()

    number <= d | d + number
    exp <= number | char("(") + sum + char(")")
    sum <= exp | exp + char("+") + sum
    start <= sum + e

    return start(s, 0)



def main():
    # PASS
    s = "(1+2+3+(4+5))"
    assert list(satisfy(s)) == [len(s)]

    s = "1"
    assert list(satisfy(s)) == [len(s)]

    s = "123"
    assert list(satisfy(s)) == [len(s)]

    s = "123+45"
    assert list(satisfy(s)) == [len(s)]

    s = "123+45+56"
    assert list(satisfy(s)) == [len(s)]

    s = "(123)"
    assert list(satisfy(s)) == [len(s)]

    s = "(123+45)+56"
    assert list(satisfy(s)) == [len(s)]

    s = "123+(45+56)"
    assert list(satisfy(s)) == [len(s)]

    s = "42+(123+45)+56"
    assert list(satisfy(s)) == [len(s)]

    s = "123+43+(45+56)"
    assert list(satisfy(s)) == [len(s)]

    s = "123+43+(45+56)+23+45"
    assert list(satisfy(s)) == [len(s)]

    s = "123+43+(45+56)+23+45"
    assert list(satisfy(s)) == [len(s)]

    s = "(123+(43))"
    assert list(satisfy(s)) == [len(s)]

    s = "(123+(43+24))"
    assert list(satisfy(s)) == [len(s)]

    s = "2+123+(123+(43+24))+(43+24)+34+67"
    assert list(satisfy(s)) == [len(s)]

    s = "7"
    assert list(satisfy(s)) == [len(s)]

    s = "12+34"
    assert list(satisfy(s)) == [len(s)]

    s = "(12+34)"
    assert list(satisfy(s)) == [len(s)]

    s = "12+(34+56)"
    assert list(satisfy(s)) == [len(s)]

    s = "(12+34)+56"
    assert list(satisfy(s)) == [len(s)]

    s = "((12+34)+56)"
    assert list(satisfy(s)) == [len(s)]

    s = "12+34+56"
    assert list(satisfy(s)) == [len(s)]

    s = "((1+2)+(3+4))"
    assert list(satisfy(s)) == [len(s)]

    s = "1+(2+(3+4))"
    assert list(satisfy(s)) == [len(s)]

    s = "((1+2)+3)+4"
    assert list(satisfy(s)) == [len(s)]

    s = "(1+(2+3))+4"
    assert list(satisfy(s)) == [len(s)]

    s = "123+(456+789)"
    assert list(satisfy(s)) == [len(s)]

    s = "(123+456)+789"
    assert list(satisfy(s)) == [len(s)]

    s = "123+(45+(6+7))"
    assert list(satisfy(s)) == [len(s)]

    s = "((123+45)+(67+89))"
    assert list(satisfy(s)) == [len(s)]

    s = "((1+2)+((3+4)+5))"
    assert list(satisfy(s)) == [len(s)]

    s = "(((1+2)+3)+(4+5))"
    assert list(satisfy(s)) == [len(s)]

    s = "(1+2)+(3+(4+5))"
    assert list(satisfy(s)) == [len(s)]

    s = "42+(7+8)+9"
    assert list(satisfy(s)) == [len(s)]

    s = "999+(1+1)"
    assert list(satisfy(s)) == [len(s)]

    s = "(999+1)+1"
    assert list(satisfy(s)) == [len(s)]

    s = "12345+(678+90)"
    assert list(satisfy(s)) == [len(s)]

    s = "12+(34+56)+78+90"
    assert list(satisfy(s)) == [len(s)]

    s = "((12+34)+56)+78"
    assert list(satisfy(s)) == [len(s)]

    s = "(12+(34+56))+78"
    assert list(satisfy(s)) == [len(s)]

    s = "((12+34)+(56+78))"
    assert list(satisfy(s)) == [len(s)]

    s = "1+2+3+4+5"
    assert list(satisfy(s)) == [len(s)]

    s = "(1+2+3)+4"
    assert list(satisfy(s)) == [len(s)]

    s = "((1+2+3)+(4+5+6))"
    assert list(satisfy(s)) == [len(s)]

    s = "1+(2+(3+(4+(5+6))))"
    assert list(satisfy(s)) == [len(s)]

    s = "1234567890+(9876543210+5)"
    assert list(satisfy(s)) == [len(s)]

    # FAILS
    s = "a"
    assert list(satisfy(s)) == []

    s = "12a"
    assert list(satisfy(s)) == []

    s = "12+"
    assert list(satisfy(s)) == []

    s = "+12"
    assert list(satisfy(s)) == []

    s = "12+56+"
    assert list(satisfy(s)) == []

    s = "12+56+45+"
    assert list(satisfy(s)) == []

    s = "+12+56+45"
    assert list(satisfy(s)) == []

    s = "12+56+(45+)"
    assert list(satisfy(s)) == []

    s = "(123"
    assert list(satisfy(s)) == []

    s = ")123"
    assert list(satisfy(s)) == []

    s = "123)"
    assert list(satisfy(s)) == []

    s = "245+34+(23+(4)"
    assert list(satisfy(s)) == []

    s = "245+34+(23+(4+7)+8))+126"
    assert list(satisfy(s)) == []

    s = "123+((45+56+3)+5))"
    assert list(satisfy(s)) == []

    s = "123+(+45+56+3)+5"
    assert list(satisfy(s)) == []

    s = "123+(45+56+3+)+5"
    assert list(satisfy(s)) == []

    s = "(1+)"
    assert list(satisfy(s)) == []

    s = "1 + 2"
    assert list(satisfy(s)) == []

    s = "1+ 2"
    assert list(satisfy(s)) == []

    s = "1 +2"
    assert list(satisfy(s)) == []

    s = " 1+2"
    assert list(satisfy(s)) == []

    s = "1+2 "
    assert list(satisfy(s)) == []

    s = "1*2"
    assert list(satisfy(s)) == []

    s = "1/2"
    assert list(satisfy(s)) == []

    s = "1(2)"
    assert list(satisfy(s)) == []

    s = "(1)2"
    assert list(satisfy(s)) == []

    s = "123+(+45)"
    assert list(satisfy(s)) == []

    s = "123+()"
    assert list(satisfy(s)) == []

    s = "123+(45+)"
    assert list(satisfy(s)) == []

    s = "(+123)+45"
    assert list(satisfy(s)) == []

    s = "123+((45+56)"
    assert list(satisfy(s)) == []

    s = "123+(45+56))"
    assert list(satisfy(s)) == []

    s = "123+)45+56("
    assert list(satisfy(s)) == []

    s = ")+("
    assert list(satisfy(s)) == []

    s = "++"
    assert list(satisfy(s)) == []


if __name__ == "__main__":
    main()


