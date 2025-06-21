from reason.core.fof_types import *
from reason.core.transform.transformer import Transformer


class Describer(Transformer):
    def __init__(self, formula):
        self.description = {Variable: set(), Const: set(), Function: set(), Predicate: set()}

        super().__init__(formula)

    def variable(self, obj, name):
        self.description[Variable].add(name)

    def const(self, obj, name):
        self.description[Const].add(name)

    def function(self, obj, name, args, targs):
        self.description[Function].add(name)

    def predicate(self, obj, name, args, targs):
        self.description[Predicate].add(name)

    def create_result(self, transformed):
        return self.description


def describe(formula):
    return Describer(formula).result
