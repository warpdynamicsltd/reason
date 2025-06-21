import os
import structlog

from pathlib import Path

from reason.core.fof_types import FirstOrderFormula
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

        self.file_stack = []
        self.logger = structlog.get_logger()

    def log(self, log_type="info", message="", formula: FirstOrderFormula = None, ast=None):
        if self.context_stack:
            L = self.current_context().L
        else:
            L = self.theory.get_langauge()

        match log_type:
            case "info":
                logger = (self.logger.info)
            case "error":
                logger = (self.logger.error)

        comment = {}
        if formula is not None:
            comment["formula"] = L.printer(formula)

        if isinstance(ast, AbstractSyntaxTree) and hasattr(ast, "meta"):
            meta = ast.meta
            comment["loc"] = dict(filename=self.current_filename(), line=meta.line, column=meta.column)

        else:
            comment["loc"] = self.current_filename()

        logger(message, **comment)


    def get_file_absolute_path(self, filename : str) -> str:
        if self.file_stack:
            return str((self.file_stack[-1].parent / filename).resolve())
        else:
            return filename

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
            res_code += transformed_line + '\n'
            # for k in line:
            #     co
        return res_code

    def current_context(self) -> Context:
        return self.context_stack[-1]

    def current_filename(self):
        if self.file_stack:
            return str(self.file_stack[-1].resolve())
        else:
            return None

    def run_expression(self, expression: AbstractSyntaxTree):
        # if hasattr(expression, "meta"):
        #     print(expression.meta.line, expression.meta.column, self.current_filename())

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
                    self.log("info", "assertion", formula=formula, ast=formula_ast)
                else:
                    formula = self.current_context().add(formula_ast)
                    self.log("info", "context assertion", formula=formula, ast=formula_ast)

                return


            case AbstractSyntaxTree(name=const.ASSUMPTION, args=[formula_ast]):
                if self.context_stack:
                    context = self.current_context()
                    formula = context.assume(formula_ast)
                    self.log("info", "context assumption", formula=formula, ast=formula_ast)
                else:
                    formula = self.theory.formula(formula_ast)
                    self.log("info", "assumption", formula=formula, ast=formula_ast)
                    self.theory.add_atomic_axiom(formula)
                return


            case AbstractSyntaxTree(name=const.CONCLUSION, args=[formula_ast]):
                context = self.current_context()
                formula = context.conclude(formula_ast)
                self.log("info", "context conclusion", formula=formula, ast=formula_ast)
                return


            case AbstractSyntaxTree(name=const.CONTEXT_BLOCK, args=expressions):
                if not self.context_stack:
                    context = Context(self.theory)

                else:
                    context = self.current_context().open_context()

                self.context_stack.append(context)

                self.log("info", "open context", ast=expression)

                self.run_expressions(expressions)

                context.close()
                self.context_stack.pop()
                self.log("info", "close context", ast=expression)
                return

            case AbstractSyntaxTree(name=const.INCLUDE_FILE, args=[s]):
                self.run_file(path=self.get_file_absolute_path(s))
                return


    def run_expressions(self, expressions : list[AbstractSyntaxTree]):
        for expression in expressions:
            self.run_expression(expression)

    def run_code(self, code : str):
        code = self.preprocess_code(code)
        program_ast_list = self.parser(code)
        self.run_expressions(program_ast_list)

    def run_file(self, path : str):
        self.file_stack.append(Path(path))
        with open(path, "r") as f:
            self.run_code(f.read())
        self.file_stack.pop()


