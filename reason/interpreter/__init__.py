from pathlib import Path
from typing import Iterable
from functools import cache

import structlog
from beartype import beartype

from reason.core.fof_types import FirstOrderFormula, Const
from reason.core.transform.base import closure
from reason.core.theory import BaseTheory, AssertionStatus
from reason.core.theory.context import Context
from reason.parser import ProgramParser, AbstractSyntaxTree
from reason.parser.tree import const
from reason.interpreter import context_exps, theory_exps


class Interpreter:
    def __init__(self, theory: BaseTheory):
        self.theory = theory
        self.parser = ProgramParser()
        self.context_stack = []

        self.file_stack = []
        self.logger = structlog.get_logger()

    @beartype
    def log(
        self,
        log_type: str = "info",
        message: str = "",
        formula: FirstOrderFormula | None = None,
        ast: AbstractSyntaxTree | None = None,
        end: bool = False
    ):
        if self.context_stack:
            L = self.current_context().L
        else:
            L = self.theory.get_langauge()

        match log_type:
            case "info":
                logger = self.logger.info
            case "error":
                logger = self.logger.error

        comment = {}
        if formula is not None:
            comment["formula"] = L.printer(closure(formula))

        if isinstance(ast, AbstractSyntaxTree) and hasattr(ast, "meta"):
            meta = ast.meta
            if not end:
                comment["loc"] = dict(filename=self.current_filename(), line=meta.line, column=meta.column)
            else:
                comment["loc"] = dict(filename=self.current_filename(), line=meta.end_line, column=meta.end_column)

        else:
            comment["loc"] = self.current_filename()

        logger(message, **comment)

    def assert_formula(self, formula_ast: AbstractSyntaxTree) -> AssertionStatus:
        if self.context_stack:
            context_exps.add_selection_axioms(self, formula_ast)
            return context_exps.assert_formula(self, formula_ast)
        else:
            theory_exps.add_selection_axioms(self, formula_ast)
            return theory_exps.assert_formula(self, formula_ast)

    def define_formula(self, formula_ast: AbstractSyntaxTree):
        if self.context_stack:
            context_exps.add_selection_axioms(self, formula_ast)
            return context_exps.define_formula(self, formula_ast)
        else:
            theory_exps.add_selection_axioms(self, formula_ast)
            return theory_exps.define_formula(self, formula_ast)

    def conclude_formula(self, formula_ast: AbstractSyntaxTree, auto_skip=False):
        if self.context_stack:
            context_exps.add_selection_axioms(self, formula_ast)
            context_exps.conclude_formula(self, formula_ast, auto_skip=auto_skip)
        else:
            theory_exps.add_selection_axioms(self, formula_ast)
            theory_exps.assert_formula(self, formula_ast)

    @beartype
    def declare_consts_with_constrain(self, formula_ast: AbstractSyntaxTree, consts: list[str]):
        context_exps.add_selection_axioms(self, formula_ast)
        context_exps.declare_consts_with_constrain(self, formula_ast, consts)

    @beartype
    def get_file_absolute_path(self, filename: str) -> str:
        if self.file_stack:
            return str((self.file_stack[-1].parent / filename).resolve())
        else:
            return filename

    @beartype
    def preprocess_code(self, code: str) -> str:
        res_code = ""
        column_translator = []
        for line_index, line in enumerate(code.split("\n")):
            index = line.find("#")
            if index != -1:
                transformed_line = line[:index]
            else:
                transformed_line = line
            # print(line)
            res_code += transformed_line + "\n"
            # for k in line:
            #     co
        return res_code

    @beartype
    def current_context(self) -> Context:
        return self.context_stack[-1]

    @beartype
    def current_filename(self) -> str | None:
        if self.file_stack:
            return str(self.file_stack[-1].resolve())
        else:
            return None

    @beartype
    def run_expression(self, expression: AbstractSyntaxTree):
        # if hasattr(expression, "meta"):
        #     print(expression.meta.line, expression.meta.column, self.current_filename())

        match expression:
            case AbstractSyntaxTree(name=const.CONST_DECLARATION, args=consts):
                context_exps.declare_consts(self, consts)
                return

            case AbstractSyntaxTree(name=const.CONST_DECLARATION_WITH_CONSTRAIN, args=[formula_ast, *consts]):
                self.declare_consts_with_constrain(formula_ast, consts)
                return

            case AbstractSyntaxTree(name=const.ATOMIC_AXIOM, args=[formula_ast]):
                if not self.context_stack:
                    theory_exps.add_atomic_axiom_formula(self, formula_ast)
                else:
                    raise RuntimeError("axioms not allowed in context")

            case AbstractSyntaxTree(name=const.ASSERTION, args=[formula_ast]):
                status = self.assert_formula(formula_ast)
                if status == AssertionStatus.null:
                    raise RuntimeError(f"not a valid assertion")
                return

            case AbstractSyntaxTree(name=const.DEFINITION, args=[formula_ast]):
                self.define_formula(formula_ast)
                return


            case AbstractSyntaxTree(name=const.ASSUMPTION, args=[formula_ast]):
                if self.context_stack:
                    context_exps.assume_formula(self, formula_ast)
                else:
                    raise RuntimeError("assumptions must be used in context")
                return

            case AbstractSyntaxTree(name=const.CONCLUSION, args=[formula_ast]):
                self.conclude_formula(formula_ast)
                return

            case AbstractSyntaxTree(name=const.CONTEXT_BLOCK, args=expressions):
                self.run_context(expression)
                return

            case AbstractSyntaxTree(
                name=const.THEOREM_CONTEXT_BLOCK,
                args=[proof_ast, theorem_ast]):
                self.run_expression(proof_ast)
                self.conclude_formula(theorem_ast, auto_skip=True)


            case AbstractSyntaxTree(name=const.INCLUDE_FILE, args=[s]):
                if self.context_stack:
                    raise RuntimeError("include not allowed in context")
                self.run_file(path=self.get_file_absolute_path(s))
                return

    @beartype
    def run_expressions(self, expressions: Iterable[AbstractSyntaxTree]):
        for expression in expressions:
            self.run_expression(expression)

    @beartype
    def run_code(self, code: str):
        code = self.preprocess_code(code)
        program_ast_list = self.parser(code)
        self.run_expressions(program_ast_list)

    @beartype
    @cache
    def run_file(self, path: str):
        self.file_stack.append(Path(path))
        with open(path, "r") as f:
            self.run_code(f.read())
        self.file_stack.pop()

    @beartype
    def run_context(self, expression: AbstractSyntaxTree):
        expressions = expression.args
        if not self.context_stack:
            context = Context(self.theory)

        else:
            context = self.current_context().open_context()

        self.context_stack.append(context)

        self.log("info", "open context", ast=expression)

        self.run_expressions(expressions)

        theorem = context.close()
        self.context_stack.pop()
        # print(expression.meta.__dict__)
        self.log("info", "close context", formula=theorem, ast=expression, end=True)
