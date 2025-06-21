from reason.core.fof_types import *


class Transformer:
    def __init__(self, formula):
        self.stack = []
        self.result = self.create_result(self._transform(formula))

    def variable(self, obj, name):
        pass

    def const(self, obj, name):
        pass

    def function(self, obj, name, args, targs):
        pass

    def predicate(self, obj, name, args, targs):
        pass

    def logic_connective(self, obj, name, args, targs):
        pass

    def logic_quantifier(self, obj, name, args, targs):
        pass

    def create_result(self, transformed):
        return transformed

    def _iter_args(self, method, obj, name, args):
        self.stack.append(obj)
        targs = []
        for arg in args:
            targ = self._transform(arg)
            targs.append(targ)

        return method(self.stack.pop(), name, args, targs)

    def _transform(self, obj):
        match obj:
            case Variable(name=name, args=args):
                return self.variable(obj, name)

            case Const(name=name, args=args):
                return self.const(obj, name)

            case Function(name=name, args=args):
                return self._iter_args(self.function, obj, name, args)

            case Predicate(name=name, args=args):
                return self._iter_args(self.predicate, obj, name, args)

            case LogicConnective(name=name, args=args):
                return self._iter_args(self.logic_connective, obj, name, args)

            case LogicQuantifier(name=name, args=args):
                return self._iter_args(self.logic_quantifier, obj, name, args)

        raise RuntimeError("unexpected type")
