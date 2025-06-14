from reason.core.theory import BaseTheory
from reason.core.theory.context import Context
from reason.parser.tree import AbstractSyntaxTree
from reason.parser.tree.consts import *
from reason.parser import ProgramParser

class Interpreter:

    def __init__(self, theory: BaseTheory):
        self.theory = theory
        self.parser = ProgramParser()
        self.context_stack = []

    def current_context(self) -> Context:
        return self.context_stack[-1]

    def execute(self, expression: AbstractSyntaxTree):
        match expression:
            case AbstractSyntaxTree(name=const.CONST_DECLARATION, args=consts):
                context = self.current_context()
                for c in consts:
                    context.declare(c)

                return


            case AbstractSyntaxTree(name=const.ASSERTION, args=[formula_ast]):
                if not self.context_stack:
                    formula = self.theory.formula(formula_ast)
                    self.theory.add_formula(formula)
                else:
                    self.current_context().add(formula_ast)

                return


            case AbstractSyntaxTree(name=const.ASSUMPTION, args=[formula_ast]):
                if self.context_stack:
                    context = self.current_context()
                    context.assume(formula_ast)
                else:
                    formula = self.theory.formula(formula_ast)
                    self.theory.add_atomic_axiom(formula)
                return


            case AbstractSyntaxTree(name=const.CONCLUSION, args=[formula_ast]):
                context = self.current_context()
                context.conclude(formula_ast)
                return


            case AbstractSyntaxTree(name=const.CONTEXT_BLOCK, args=expressions):
                if not self.context_stack:
                    context = Context(self.theory)

                else:
                    context = self.current_context().open_context()

                self.context_stack.append(context)

                self.run(expressions)

                context.close()
                self.context_stack.pop()
                return

            case AbstractSyntaxTree(name=const.INCLUDE_FILE, args=[s]):
                with open(s, "r") as f:
                    code = f.read()

                program_ast_list = self.parser(code)
                self.run(program_ast_list)


    def run(self, expressions : list[AbstractSyntaxTree]):
        for expression in expressions:
            self.execute(expression)

    def __call__(self, expressions : list[AbstractSyntaxTree]):
        self.run(expressions)
        print("\nQUOD ERAT DEMONSTRANDUM")

