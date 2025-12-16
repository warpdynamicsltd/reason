"""
Substitution transformations for first-order formulas.

This module implements predicate substitution, which replaces occurrences of a
predicate pattern with a formula while maintaining proper variable scoping.
"""

from reason.core.fof_types import (
    FirstOrderFormula,
    LogicConnective,
    LogicQuantifier,
    Predicate,
    Term,
    Variable,
)
from reason.parser.tree.consts import *


class NotAdmissibleError(Exception):
    """Raised when a substitution would capture free variables."""
    pass


def free_variables_in_term(term: Term) -> set[Variable]:
    """
    Compute the set of free variables in a term.

    Args:
        term: A Term (Variable, Const, or Function)

    Returns:
        Set of Variable objects that occur free in the term
    """
    match term:
        case Variable(name=name):
            return {Variable(name)}
        case term if hasattr(term, 'args'):
            result = set()
            for arg in term.args:
                result.update(free_variables_in_term(arg))
            return result
        case _:
            return set()


def free_variables_in_formula(formula: FirstOrderFormula) -> set[Variable]:
    """
    Compute the set of free variables in a formula.

    Args:
        formula: A FirstOrderFormula

    Returns:
        Set of Variable objects that occur free in the formula
    """
    match formula:
        case Predicate(name=_, args=args):
            result = set()
            for term in args:
                result.update(free_variables_in_term(term))
            return result

        case LogicConnective(name=_, args=args):
            result = set()
            for arg in args:
                result.update(free_variables_in_formula(arg))
            return result

        case LogicQuantifier(name=_, args=[var, body]):
            vars_in_body = free_variables_in_formula(body)
            # Remove the bound variable
            vars_in_body.discard(var)
            return vars_in_body

        case _:
            return set()


def create_substitution_map(pattern_vars: list[Term], actual_args: list[Term]) -> dict[str, Term]:
    """
    Create a substitution map from pattern variables to actual arguments.

    Args:
        pattern_vars: List of variables in the predicate pattern
        actual_args: List of actual arguments to substitute for

    Returns:
        Dictionary mapping variable names to terms

    Raises:
        NotAdmissibleError: If pattern_vars contains non-variables or has duplicates
    """
    if len(pattern_vars) != len(actual_args):
        raise NotAdmissibleError("Pattern and arguments must have the same length")

    subst_map = {}
    for pattern_var, actual_arg in zip(pattern_vars, actual_args):
        if not isinstance(pattern_var, Variable):
            raise NotAdmissibleError("Pattern must contain only variables")

        var_name = pattern_var.name
        if var_name in subst_map:
            raise NotAdmissibleError("Duplicate variable in pattern")

        subst_map[var_name] = actual_arg

    return subst_map


def apply_substitution_to_term(subst_map: dict[str, Term], term: Term) -> Term:
    """
    Apply a substitution map to a term.

    Args:
        subst_map: Dictionary mapping variable names to replacement terms
        term: Term to substitute into

    Returns:
        The term with substitutions applied
    """
    match term:
        case Variable(name=name):
            return subst_map.get(name, term)

        case term if hasattr(term, 'args'):
            new_args = [apply_substitution_to_term(subst_map, arg) for arg in term.args]
            return type(term)(term.name, *new_args)

        case _:
            return term


def apply_substitution_to_formula(subst_map: dict[str, Term], formula: FirstOrderFormula) -> FirstOrderFormula:
    """
    Apply a substitution map to a formula.

    Args:
        subst_map: Dictionary mapping variable names to replacement terms
        formula: Formula to substitute into

    Returns:
        The formula with substitutions applied

    Raises:
        NotAdmissibleError: If substitution would capture a variable
    """
    match formula:
        case Predicate(name=name, args=args):
            new_args = [apply_substitution_to_term(subst_map, arg) for arg in args]
            return Predicate(name, *new_args)

        case LogicConnective(name=name, args=args):
            new_args = [apply_substitution_to_formula(subst_map, arg) for arg in args]
            return LogicConnective(name, *new_args)

        case LogicQuantifier(name=quantifier, args=[var, body]):
            # Check if any term in the substitution map contains the bound variable
            # If so, the substitution is not admissible
            var_name = var.name
            for _, term in subst_map.items():
                if var in free_variables_in_term(term):
                    raise NotAdmissibleError(
                        f"Substitution would capture variable {var_name}"
                    )

            # Remove the bound variable from the substitution map for the body
            new_map = {k: v for k, v in subst_map.items() if k != var_name}
            new_body = apply_substitution_to_formula(new_map, body)
            return LogicQuantifier(quantifier, var, new_body)

        case _:
            return formula


def substitute_predicate(
    predicate: Predicate,
    replacement: FirstOrderFormula,
    formula: FirstOrderFormula
) -> FirstOrderFormula:
    """
    Substitute occurrences of a predicate pattern with a formula.

    This function replaces all occurrences of a predicate that match the given
    pattern with the replacement formula. The pattern variables are substituted
    with the actual arguments in each occurrence.

    Args:
        predicate: A Predicate pattern (e.g., Predicate("P", Variable("x"), Variable("y")))
                  The predicate must have only Variable arguments.
        replacement: The formula to substitute in place of matching predicates
        formula: The formula to perform substitution on

    Returns:
        The formula with all matching predicate occurrences replaced

    Raises:
        NotAdmissibleError: If the substitution would capture free variables,
                           or if the predicate pattern is malformed

    Example:
        >>> # Substitute P(x, y) with Q(x, y) & R(x, y)
        >>> pattern = Predicate("P", Variable("x"), Variable("y"))
        >>> replacement = LogicConnective("AND",
        ...                               Predicate("Q", Variable("x"), Variable("y")),
        ...                               Predicate("R", Variable("x"), Variable("y")))
        >>> formula = Predicate("P", Variable("a"), Variable("b"))
        >>> result = substitute_predicate(pattern, replacement, formula)
        >>> # result is: Q(a, b) & R(a, b)
    """
    # Extract predicate name and pattern variables
    if not isinstance(predicate, Predicate):
        raise NotAdmissibleError("Pattern must be a Predicate")

    pred_name = predicate.name
    pred_vars = list(predicate.args)

    # Validate that all pattern arguments are variables
    for var in pred_vars:
        if not isinstance(var, Variable):
            raise NotAdmissibleError("Predicate pattern must contain only variables")

    # Compute free variables in the replacement formula
    free_in_replacement = free_variables_in_formula(replacement)

    def subst_pred(bound_vars: set[Variable], f: FirstOrderFormula) -> FirstOrderFormula:
        """
        Recursively substitute predicates, tracking bound variables.

        Args:
            bound_vars: Set of variables that are currently bound by quantifiers
            f: Formula to process

        Returns:
            The formula with substitutions applied
        """
        match f:
            case Predicate(name=name, args=args) if name == pred_name and len(args) == len(pred_vars):
                # This predicate matches the pattern
                # Create substitution map from pattern variables to actual arguments
                subst_map = create_substitution_map(pred_vars, args)

                # Get the set of variables that are in the substitution map
                vars_in_map = {Variable(var_name) for var_name in subst_map.keys()}

                # Apply the substitution to the replacement formula
                substituted = apply_substitution_to_formula(subst_map, replacement)

                # Check that no free variables in replacement (excluding those in the map)
                # would be captured by bound variables
                free_excluding_map_vars = free_in_replacement - vars_in_map
                for var in free_excluding_map_vars:
                    if var in bound_vars:
                        raise NotAdmissibleError(
                            f"Substitution would capture free variable {var.name}"
                        )

                return substituted

            case Predicate(name=name, args=args):
                # Predicate doesn't match the pattern
                return Predicate(name, *args)

            case LogicConnective(name=name, args=args):
                new_args = [subst_pred(bound_vars, arg) for arg in args]
                return LogicConnective(name, *new_args)

            case LogicQuantifier(name=quantifier, args=[var, body]):
                # Add this variable to the bound set
                new_bound_vars = bound_vars | {var}
                new_body = subst_pred(new_bound_vars, body)
                return LogicQuantifier(quantifier, var, new_body)

            case _:
                return f

    return subst_pred(set(), formula)