from abc import ABC, abstractmethod
from typing import List, Generator, Iterator
from reason.core.fof import *
from reason.core.theory.tautology import prove, Tautology
from reason.core.theory import BaseTheory, AssertionStatus
from reason.core.transform.base import remove_universal_quantifiers, conjunction, closure
from reason.core.transform.describe import describe
from reason.parser.tree.consts import *
from reason.core.language import Language, derive
from reason.parser.tree import AbstractSyntaxTree


class Context:
    def __init__(self, theory: BaseTheory, L: Language | None = None, const_index: int = 0, name: str = "0"):
        self.name = name
        self.theory = theory

        self.context_const_index = const_index
        self.context_theory_stack_start = self.theory.get_stack_len()

        # self.const_map = {}
        # self.const_map_inv = {}
        self.const_values = set()
        self.local_const_values = set()
        if L is None:
            self.L = self.theory.derive_language()
        else:
            self.L = L
        self.premises = []
        self.conclusions = []

    @staticmethod
    def const_name(index: int):
        return f"local_const_{index}"

    def declare(self, c: str) -> str:
        # self.const_map[c] = self.context_const_index
        # self.const_map_inc[self.context_const_index] = c
        # c_value = self.const_name(self.context_const_index)
        c_value = f"{self.name}_{c}"
        self.L.add_const(c, c_value=c_value)
        # self.L.add_const(c_value, c_value=c_value)
        self.const_values.add(c_value)
        self.context_const_index += 1
        return c_value

    def assume(self, s: str | AbstractSyntaxTree) -> FirstOrderFormula:
        if isinstance(s, AbstractSyntaxTree):
            formula = self.L.to_formula(s)
        else:
            formula = self.L(s)

        formula = closure(formula)
        self.premises.append(formula)
        self.theory._push(formula)
        return formula

    def add(self, s: str | AbstractSyntaxTree) -> tuple[FirstOrderFormula, AssertionStatus]:
        if isinstance(s, AbstractSyntaxTree):
            formula = self.L.to_formula(s)
        else:
            formula = self.L(s)
        formula, status = self.theory.add_formula(formula)
        return formula, status

    def define(self, s: str | AbstractSyntaxTree) -> FirstOrderFormula:
        if isinstance(s, AbstractSyntaxTree):
            formula = self.L.to_formula(s)
        else:
            formula = self.L(s)
        return self.theory.add_definition(formula)

    def declare_consts_with_constrain(self, s: str | AbstractSyntaxTree, consts: list[str]) -> FirstOrderFormula:
        c_values = []
        for c in consts:
            c_value = self.declare(c)
            c_values.append(c_value)
            self.local_const_values.add(c_value)


        if isinstance(s, AbstractSyntaxTree):
            formula = self.L.to_formula(s)
        else:
            formula = self.L(s)

        return self.theory.declare_consts_with_constrain(formula, [self.L.consts[c] for c in consts])

    def conclude(self, s: str | AbstractSyntaxTree, auto_skip=False) -> tuple[FirstOrderFormula, AssertionStatus]:
        formula, status = self.add(s)
        description = describe(formula)

        if auto_skip and len(self.local_const_values.intersection(description[Const])) > 0:
            return formula, status

        self.conclusions.append(formula)
        return formula, status

    def close(self) -> FirstOrderFormula:
        context_produced = self.theory.get_stack_len() - self.context_theory_stack_start
        if context_produced:
            while self.theory.get_stack_len() > self.context_theory_stack_start:
                self.theory._pop()

            if self.premises:
                theorem = LogicConnective(IMP, conjunction(*self.premises), conjunction(*self.conclusions))
            else:
                theorem = conjunction(*self.conclusions)

            description = describe(theorem)
            for c in description[Const]:
                if c in self.local_const_values:
                    raise RuntimeError(f"const {c} is bound to the context")
                if c in self.const_values:
                    theorem = theorem.replace(Const(c), Variable(c))

            description = describe(theorem)

            for p in description[Predicate]:
                if not self.theory.is_used(Predicate, p):
                    raise RuntimeError(f"unseen predicate {p}")

            for f in description[Function]:
                if not self.theory.is_used(Function, f):
                    raise RuntimeError(f"unseen function {f}")

            self.theory._push(theorem)
            return theorem

        raise SyntaxError("context without conclusions")

    def open_context(self):
        return Context(
            theory=self.theory, L=derive(self.L), name=str(int(self.name) + 1), const_index=self.context_const_index
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
