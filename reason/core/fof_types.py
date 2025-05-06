from reason.core import AbstractTerm


class Term(AbstractTerm):
    pass


class Variable(Term):
    pass


class Const(Term):
    pass


class Function(Term):
    pass


class FirstOrderFormula(AbstractTerm):
    pass


class Predicate(FirstOrderFormula):
    pass


class LogicPredicate(FirstOrderFormula):
    pass


class LogicConnective(LogicPredicate):
    pass


class LogicQuantifier(LogicPredicate):
    pass