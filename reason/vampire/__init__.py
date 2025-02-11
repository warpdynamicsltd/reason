import re
import logging

from importlib.resources import files
from reason.tools.binary import run_binary
from reason.vampire.translator import to_fof

__version__ = "0.1.0"


class Vampire:
    @staticmethod
    def exec(input, **kwargs):
        bin_path = files("reason") / "assets" / "bin" / "vampire"

        args = []
        for key in kwargs:
            args.append(f"--{key}")
            args.append(kwargs[key])

        return run_binary(str(bin_path), input, *args)

    @staticmethod
    def formula_to_fof_line(formula, name="formula", type="conjecture"):
        res = f"fof({name},{type},{to_fof(formula)})."
        return res

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.lines = []

    def __call__(self, formula):
        lines = list(self.lines)
        line = self.formula_to_fof_line(formula)
        lines.append(line)

        if self.verbose:
            for l in lines:
                print(l)

        res = self.exec("\n".join(lines))
        for line in res.split("\n"):
            if self.verbose:
                print(line)
            if line and line[0] != "%":
                m = re.search(r"\$false", line)
                if m:
                    return True

        return False

    def add_formula(self, formula, name, type):
        if self.verbose:
            print(formula)
        fof_line = self.formula_to_fof_line(formula, name=name, type=type)
        if self.verbose:
            print(fof_line)
        self.lines.append(fof_line)

    def add_axiom(self, formula, name):
        self.add_formula(formula, name, type="axiom")
