from typing import Tuple

from reason.core.fof_types import Const, FirstOrderFormula, Function, LogicConnective, LogicPredicate, LogicQuantifier, Predicate, Term, Variable
from reason.core.transform.base import prepend_quantifier_signature
from reason.parser.tree import AbstractSyntaxTree


def conjunction(*formulas: list[FirstOrderFormula]):
    if len(formulas) == 1:
        return formulas[0]
    
    #formulas = list(reversed(formulas))
    
    res = formulas[0]
    for f in formulas[1:]:
        res = LogicConnective("AND", res, f)

    return res

class FormulaBuilder:
    def __init__(self, consts: dict[str, str], select_vars_prefix="u"):
        self.consts = consts
        self.select_vars_count = 0
        self.select_vars_prefix = select_vars_prefix

    @staticmethod
    def unflatten_conjunctions(ast: AbstractSyntaxTree) -> AbstractSyntaxTree:
        match ast:
            case AbstractSyntaxTree(name="CONJUNCTION"):
                return ast.flat_to_tree("AND")

        return ast
    
    def process_selector(self, index_tree: AbstractSyntaxTree, selector_tree: AbstractSyntaxTree, embedded_selectors: list = []) -> Variable:
        index_formula, embedded_selectors_index = self.process(index_tree)
        selector_formula, _ = self.process(selector_tree)
        embedded_selectors.extend(embedded_selectors_index)
        match index_formula:
            case Predicate(name="IN", args=[v, t]) if type(v) is Variable and isinstance(t, Term):
                self.select_vars_count += 1
                selector_var = Variable(f"{self.select_vars_prefix}{self.select_vars_count}")
                embedded_selectors.append((selector_var, v, t, selector_formula))
                return selector_var
                
        raise Exception("formula can't be parsed")

    def process(
        self, 
        ast: AbstractSyntaxTree,
        parent_type: type = None,
        embedded_selectors: list = []
    ) -> Tuple[FirstOrderFormula | Const | Variable | Function, list]:
        embedded_selectors = list(embedded_selectors)
        ast = self.unflatten_conjunctions(ast)
        match ast:
            case AbstractSyntaxTree(name=name) if name in {"OR", "AND", "NEG", "IMP", "IFF"}:
                return LogicConnective(name, *map(lambda a: self.process(a, LogicConnective)[0], ast.args)), []

            case AbstractSyntaxTree(name=name, args=[variable, arg]) if name in {"FORALL", "EXISTS"}:
                return LogicQuantifier(name, Variable(variable.name), self.process(arg, LogicQuantifier)[0]), []

            case AbstractSyntaxTree(name=name) if (
                parent_type in {LogicConnective, LogicQuantifier} or parent_type is None
            ):
                _args = []
                for arg in ast.args:
                    f, _embedded_selectors = self.process(arg, Predicate)
                    _args.append(f)
                    embedded_selectors.extend(_embedded_selectors)
                    k = 7

                formulas = []
                quantifier_signature = []
                for selector_var, v, t, selector_formula in embedded_selectors:
                    f = LogicQuantifier(
                        "FORALL",
                        v,
                        LogicConnective(
                            "IFF",
                            Predicate("IN", v, selector_var),
                            LogicConnective(
                                "AND",
                                Predicate("IN", v, t),
                                selector_formula
                            )
                        )
                    )
                    formulas.append(f)
                    quantifier_signature.append(("EXISTS", selector_var))

                result_formula = conjunction(Predicate(name, *_args), *formulas)
                result_formula = prepend_quantifier_signature(result_formula, quantifier_signature)

                return result_formula, []

            case AbstractSyntaxTree(name=x, args=[]):
                if x in self.consts:
                    return Const(name=self.consts[x]), []
                else:
                    return Variable(name=x), []
                
            case AbstractSyntaxTree(name="SELECT", args=[index_tree, selector_tree]):
                return self.process_selector(index_tree, selector_tree, embedded_selectors), embedded_selectors

        _args = []
        for arg in ast.args:
            f, _embedded_selectors = self.process(arg, Function)
            _args.append(f)
            embedded_selectors.extend(_embedded_selectors)

        return Function(ast.name, *_args), embedded_selectors

    def __call__(self, ast: AbstractSyntaxTree) -> FirstOrderFormula:
        return self.process(ast)[0]

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

            case LogicConnective(args=args):
                return all(
                    self.well_formed(arg) and type(arg) in {Predicate, LogicConnective, LogicQuantifier} for arg in args
                )

            case LogicQuantifier(args=[variable, arg]):
                return (
                    type(variable) is Variable
                    and self.well_formed(variable)
                    and type(arg) in {Predicate, LogicConnective, LogicQuantifier}
                    and self.well_formed(arg)
                )

        return False
