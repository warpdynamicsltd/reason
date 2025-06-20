import re
import logging

from importlib.resources import files
from reason.tools.binary import run_binary
from reason.vampire.translator import to_tptp_fof

__version__ = "0.1.0"


class Vampire:
    @staticmethod
    def exec(input, **kwargs):
        bin_path = files("reason") / "assets" / "bin" / "vampire"

        args = []
        for key in kwargs:
            args.append(f"--{key}")
            if kwargs[key] is not None:
                args.append(kwargs[key])

        return run_binary(str(bin_path), input, *args)

    @staticmethod
    def formula_to_fof_line(formula, name="formula", type="conjecture"):
        res = f"fof({name},{type},{to_tptp_fof(formula)})."
        return res

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.lines = {}

    def compile_input(self, formula):
        lines = list(self.lines.values())
        line = self.formula_to_fof_line(formula)
        lines.append(line)

        if self.verbose:
            for l in lines:
                print(l)

        return "\n".join(lines)

    def run(self, formula, **kwargs):
        input_str = self.compile_input(formula)

        res = self.exec(input_str, **kwargs)
        return res

    def __call__(self, formula):
        input_str = self.compile_input(formula)

        res = self.exec(input_str)
        for line in res.split("\n"):
            if self.verbose:
                print(line)
            if line == "% Termination reason: Refutation":
                return True

        return False

    def add_formula(self, formula, name, type):
        if self.verbose:
            print(formula)
        fof_line = self.formula_to_fof_line(formula, name=name, type=type)
        if self.verbose:
            print(fof_line)
        self.lines[name] = fof_line

    def add_axiom(self, formula, name):
        self.add_formula(formula, name, type="axiom")
