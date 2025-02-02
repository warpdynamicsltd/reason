from reason.core import AbstractTerm
from reason.parser.tree import AbstractSyntaxTree


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


class FormulaBuilder:
    def __init__(self, consts: dict[str, str]):
        self.consts = consts

    @staticmethod
    def unflatten_conjunctions(ast: AbstractSyntaxTree) -> AbstractSyntaxTree:
        match ast:
            case AbstractSyntaxTree(name="CONJUNCTION"):
                return ast.flat_to_tree("AND")

        return ast

    def process(
        self, ast: AbstractSyntaxTree, parent_type: type = None
    ) -> FirstOrderFormula | Const | Variable | Function:
        ast = self.unflatten_conjunctions(ast)
        match ast:
            case AbstractSyntaxTree(name=x, args=[]):
                if x in self.consts:
                    return Const(name=self.consts[x])
                else:
                    return Variable(name=x)

            case AbstractSyntaxTree(name=name) if name in {"OR", "AND", "NEG", "IMP", "IFF"}:
                return LogicConnective(name, *map(lambda a: self.process(a, LogicConnective), ast.args))

            case AbstractSyntaxTree(name=name) if name in {"FORALL", "EXISTS"}:
                return LogicQuantifier(name, *map(lambda a: self.process(a, LogicQuantifier), ast.args))

            case AbstractSyntaxTree(name=name) if (
                parent_type in {LogicConnective, LogicQuantifier} or parent_type is None
            ):
                return Predicate(name, *map(lambda a: self.process(a, Predicate), ast.args))

        return Function(ast.name, *map(lambda a: self.process(a, Function), ast.args))

    def __call__(self, ast: AbstractSyntaxTree) -> FirstOrderFormula:
        return self.process(ast)

    def well_formed(self, obj: Const | Variable | Predicate | Function | LogicPredicate | FirstOrderFormula) -> bool:
        match obj:
            case Variable(name=name, args=args):
                return type(name) is str and not args

            case Const(name=name, args=args):
                return type(name) is str and not args

            case Function(name=name, args=args):
                return type(name) is str and all(self.well_formed(arg) and isinstance(arg, Term) for arg in args)

            case Predicate(name=name, args=args):
                return type(name) is str and all(self.well_formed(arg) and isinstance(arg, Term) for arg in args)

            case LogicConnective(name=name, args=args):
                return all(
                    self.well_formed(arg) and type(arg) in {Predicate, LogicConnective, LogicQuantifier} for arg in args
                )

            case LogicQuantifier(name=name, args=[variable, arg]):
                return (
                    type(variable) is Variable
                    and self.well_formed(variable)
                    and type(arg) in {Predicate, LogicConnective, LogicQuantifier}
                    and self.well_formed(arg)
                )

        return False
