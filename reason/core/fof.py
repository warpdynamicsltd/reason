from functools import cache
from reason.core.fof_types import (
    Const,
    FirstOrderFormula,
    Function,
    LogicConnective,
    LogicPredicate,
    LogicQuantifier,
    Predicate,
    Term,
    Variable,
)
from reason.core.transform.base import prepend_quantifier_signature, conjunction, free_variables
from reason.parser.tree import AbstractSyntaxTree
from reason.parser.tree.consts import *


class FormulaBuilder:
    selector_name_index = 0

    @staticmethod
    @cache
    def get_selector_name(index_formula, selector_formula):
        FormulaBuilder.selector_name_index += 1
        return f"sel{FormulaBuilder.selector_name_index}"

    def __init__(self, ast: AbstractSyntaxTree, consts: dict[str, str] = {}, select_vars_prefix="u"):
        self.consts = consts
        self.select_vars_count = 0
        self.select_vars_prefix = select_vars_prefix
        self.axioms = []
        self.formula = self._transform(ast)

    @staticmethod
    def unflatten_conjunctions(ast: AbstractSyntaxTree) -> AbstractSyntaxTree:
        match ast:
            case AbstractSyntaxTree(name=const.CONJUNCTION):
                return ast.flat_to_tree(AND)

        return ast

    def _transform_selector(
        self, index_tree: AbstractSyntaxTree, selector_tree: AbstractSyntaxTree
    ) -> Function:
        index_formula = self._transform(index_tree)
        selector_formula = self._transform(selector_tree)

        index_free_variables = free_variables(selector_formula)
        selector_free_variables = free_variables(selector_formula)
        variables = index_free_variables.union(selector_free_variables)

        match index_formula:
            case Predicate(name=const.IN, args=[v, t]) if type(v) is Variable and isinstance(t, Term):
                variables.remove(v)
                if variables:
                    transformed_selector_formula = Function(self.get_selector_name(index_formula, selector_formula), *variables)
                else:
                    transformed_selector_formula = Const(self.get_selector_name(index_formula, selector_formula))

                f = LogicQuantifier(
                    FORALL,
                    v,
                    LogicConnective(
                        IFF,
                        Predicate(IN, v, transformed_selector_formula),
                        LogicConnective(AND, Predicate(IN, v, t), selector_formula),
                    ),
                )

                self.axioms.append(f)

                return transformed_selector_formula

        raise RuntimeError("formula can't be parsed")


    def _transform(
        self, ast: AbstractSyntaxTree, parent_type: type = None
    ) -> FirstOrderFormula | Const | Variable | Function:
        match ast:
            case AbstractSyntaxTree(name=name) if name in {OR, AND, NEG, IMP, IFF}:
                return LogicConnective(name, *map(lambda a: self._transform(a, LogicConnective), ast.args))

            case AbstractSyntaxTree(name=name, args=[variable, arg]) if name in {FORALL, EXISTS}:
                return LogicQuantifier(name, Variable(variable.name), self._transform(arg, LogicQuantifier))

            case AbstractSyntaxTree(name=name) if (
                parent_type in {LogicConnective, LogicQuantifier} or parent_type is None
            ):
                return Predicate(name, *map(lambda a: self._transform(a, Predicate), ast.args))

            case AbstractSyntaxTree(name=x, args=[]):
                if x in self.consts:
                    return Const(name=self.consts[x])
                else:
                    return Variable(name=x)

            case AbstractSyntaxTree(name=const.SELECT, args=[index_tree, selector_tree]):
                return self._transform_selector(index_tree, selector_tree)

        return Function(ast.name, *map(lambda a: self._transform(a, Function), ast.args))

    def _well_formed(self, obj: Const | Variable | Predicate | Function | LogicPredicate | FirstOrderFormula) -> bool:
        match obj:
            case Variable(name=name, args=args):
                return type(name) is str and not args

            case Const(name=name, args=args):
                return type(name) is str and not args

            case Function(name=name, args=args):
                return type(name) is str and all(self._well_formed(arg) and isinstance(arg, Term) for arg in args)

            case Predicate(name=name, args=args):
                return type(name) is str and all(self._well_formed(arg) and isinstance(arg, Term) for arg in args)

            case LogicConnective(args=args):
                return all(
                    self._well_formed(arg) and type(arg) in {Predicate, LogicConnective, LogicQuantifier}
                    for arg in args
                )

            case LogicQuantifier(args=[variable, arg]):
                return (
                    type(variable) is Variable
                    and self._well_formed(variable)
                    and type(arg) in {Predicate, LogicConnective, LogicQuantifier}
                    and self._well_formed(arg)
                )

        return False

    def well_formed(self):
        return self._well_formed(self.formula)
