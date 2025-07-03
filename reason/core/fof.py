from typing import Tuple

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
    def get_selector_name():
        FormulaBuilder.selector_name_index += 1
        return f"sel{FormulaBuilder.selector_name_index}"

    def __init__(self, ast: AbstractSyntaxTree, consts: dict[str, str] = {}, select_vars_prefix="u"):
        self.consts = consts
        self.select_vars_count = 0
        self.select_vars_prefix = select_vars_prefix
        self.axioms = []
        self.formula = self._transform(ast)[0]

    @staticmethod
    def unflatten_conjunctions(ast: AbstractSyntaxTree) -> AbstractSyntaxTree:
        match ast:
            case AbstractSyntaxTree(name=const.CONJUNCTION):
                return ast.flat_to_tree(AND)

        return ast

    def _transform_selector(
        self, index_tree: AbstractSyntaxTree, selector_tree: AbstractSyntaxTree, embedded_selectors: list = []
    ) -> Function:
        index_formula, embedded_selectors_index = self._transform(index_tree)
        selector_formula, _ = self._transform(selector_tree)

        index_free_variables = free_variables(selector_formula)
        selector_free_variables = free_variables(selector_formula)
        variables = index_free_variables.union(selector_free_variables)

        embedded_selectors.extend(embedded_selectors_index)
        match index_formula:
            case Predicate(name=const.IN, args=[v, t]) if type(v) is Variable and isinstance(t, Term):
                variables.remove(v)
                if variables:
                    transformed_selector_formula = Function(self.get_selector_name(), *variables)
                else:
                    transformed_selector_formula = Const(self.get_selector_name())
                # embedded_selectors.append((transformed_selector_formula, v, t, selector_formula))

                f = LogicQuantifier(
                    FORALL,
                    v,
                    LogicConnective(
                        IFF,
                        Predicate(IN, v, transformed_selector_formula),
                        LogicConnective(AND, Predicate(IN, v, t), selector_formula),
                    ),
                )
                # formulas.append(f)
                self.axioms.append(f)

                return transformed_selector_formula

        raise RuntimeError("formula can't be parsed")

    # def _transform_selectors_to_predicate(
    #     self, ast: AbstractSyntaxTree, name: str, embedded_selectors: list
    # ) -> FirstOrderFormula:
    #     _args = []
    #     for arg in ast.args:
    #         f, _embedded_selectors = self._transform(arg, Predicate)
    #         _args.append(f)
    #         embedded_selectors.extend(_embedded_selectors)
    #
    #     # formulas = []
    #     axioms = []
    #     quantifier_signature = []
    #     for transformed_selector_formula, v, t, selector_formula in embedded_selectors:
    #         f = LogicQuantifier(
    #             FORALL,
    #             v,
    #             LogicConnective(
    #                 IFF,
    #                 Predicate(IN, v, transformed_selector_formula),
    #                 LogicConnective(AND, Predicate(IN, v, t), selector_formula),
    #             ),
    #         )
    #         # formulas.append(f)
    #         axioms.append(f)
    #
    #     self.axioms.extend(axioms)
    #     result_formula = Predicate(name, *_args)
    #
    #     return result_formula

    def _transform_args_and_update_embedded_selectors(self, ast: AbstractSyntaxTree, embedded_selectors: list):
        _args = []
        for arg in ast.args:
            f, _embedded_selectors = self._transform(arg, Function)
            _args.append(f)
            embedded_selectors.extend(_embedded_selectors)

        return _args

    def _transform(
        self, ast: AbstractSyntaxTree, parent_type: type = None, embedded_selectors: list = []
    ) -> Tuple[FirstOrderFormula | Const | Variable | Function, list]:
        embedded_selectors = list(embedded_selectors)
        ast = self.unflatten_conjunctions(ast)
        match ast:
            case AbstractSyntaxTree(name=name) if name in {OR, AND, NEG, IMP, IFF}:
                return LogicConnective(name, *map(lambda a: self._transform(a, LogicConnective)[0], ast.args)), []

            case AbstractSyntaxTree(name=name, args=[variable, arg]) if name in {FORALL, EXISTS}:
                return LogicQuantifier(name, Variable(variable.name), self._transform(arg, LogicQuantifier)[0]), []

            case AbstractSyntaxTree(name=name) if (
                parent_type in {LogicConnective, LogicQuantifier} or parent_type is None
            ):
                #return self._transform_selectors_to_predicate(ast, name, embedded_selectors), []
                return Predicate(name, *map(lambda a: self._transform(a, Predicate)[0], ast.args)), []

            case AbstractSyntaxTree(name=x, args=[]):
                if x in self.consts:
                    return Const(name=self.consts[x]), []
                else:
                    return Variable(name=x), []

            case AbstractSyntaxTree(name=const.SELECT, args=[index_tree, selector_tree]):
                return self._transform_selector(index_tree, selector_tree, embedded_selectors), embedded_selectors

        return Function(
            ast.name, *self._transform_args_and_update_embedded_selectors(ast, embedded_selectors)
        ), embedded_selectors

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
