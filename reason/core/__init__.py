from typing import Self
from beartype import beartype


class MutateImmutableError(Exception):
    pass


class NotAcceptedType(Exception):
    pass


# @beartype
class AbstractTerm:
    def __init__(self, name: str | int | tuple, *args: Self | str | int | tuple):
        self.__name = name
        self.__args = tuple(args)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, v):
        raise MutateImmutableError()

    @property
    def args(self):
        return self.__args

    @args.setter
    def args(self, args):
        raise MutateImmutableError()

    def __hash__(self):
        if not self.args:
            return hash((type(self), self.name))
        else:
            return hash((type(self), self.name, *self.args))

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name and self.args == other.args

    def replace(self, source, target):
        new_args = []
        for arg in self.args:
            if arg == source:
                new_arg = target
            elif isinstance(arg, AbstractTerm):
                new_arg = arg.replace(source, target)
            else:
                new_arg = arg

            new_args.append(new_arg)

        return type(self)(self.name, *new_args)

    def show(self):
        if self.args:
            return f"{type(self).__name__}({self.name}, {', '.join(map(AbstractTerm.show, self.args))})"
        else:
            return f"{type(self).__name__}({self.name})"

    def __repr__(self):
        if self.args:
            return f"{self.name}({', '.join(map(repr, self.args))})"
        else:
            return f"{self.name}"


class Variable(AbstractTerm):
    pass


class Const(AbstractTerm):
    pass


class Formula(AbstractTerm):
    pass


class AbstractTermMutable:
    def __init__(self, name, *args):
        self.name = name
        self.args = list(args)

    @classmethod
    def immutable_copy(cls, obj: Self | str | int | tuple, T: type):
        if isinstance(obj, AbstractTermMutable):
            return T(obj.name, *map(lambda a: cls.immutable_copy(a, T), obj.args))
        else:
            return obj


def n_nodes(term):
    if isinstance(term, AbstractTerm):
        return sum(map(n_nodes, term.args)) + 1
    else:
        return 1
