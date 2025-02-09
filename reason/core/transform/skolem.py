from reason.core.fof import *


def expand_iff(formula):
    match formula:
        case LogicConnective(name="IFF", args=[a, b]):
            return LogicConnective(
                "AND",
                LogicConnective("IMP", expand_iff(a), expand_iff(b)),
                LogicConnective("IMP", expand_iff(b), expand_iff(a)),
            )

        case AbstractTerm(name=name, args=args):
            type(formula)(name, *map(expand_iff, args))

    return formula


class UniqueVariables:
    def __init__(self):
        self.variable_index = 1

    def __call__(self, formula):
        match formula:
            case LogicQuantifier(name=op, args=[var, arg]):
                _var = Variable(f"x{self.variable_index}")
                self.variable_index += 1
                return LogicQuantifier(op, _var, self(arg.replace(var, _var)))

            case AbstractTerm(name=name, args=args):
                return type(formula)(name, *map(self.__call__, args))

        return formula


# def skolem(formula):
#     match formula:
