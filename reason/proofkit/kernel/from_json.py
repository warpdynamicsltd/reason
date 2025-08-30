from reason.core.fof_types import *

def from_json(json_obj: dict):
    match json_obj:
        # Handling Variables
        case {"type": "Variable", "name": name}:
            return Variable(name)

        # Handling Constants
        case {"type": "Const", "name": name}:
            return Const(name)

        case {"type": "ContextConst", "name": name}:
            return Const(f"context_{name}")

        case {"type": "SkolemConst", "args": args}:
            return Const(f"skolem_{"_".join(map(str, args))}")

        # Handling Functions
        case {"type": "Function", "name": name, "args": args}:
            arguments = [from_json(arg) for arg in args]
            return Function(name, *arguments)

        # Handling Predicates
        case {"type": "Predicate", "name": name, "args": args}:
            arguments = [from_json(arg) for arg in args]
            return Predicate(name, *arguments)

        # Handling LogicConnectives
        case {"type": "LogicConnective", "name": name, "args": [f]} if name == "NEG":
            return LogicConnective(name, from_json(f))

        case {"type": "LogicConnective", "name": name, "args": [left, right]} if name in {"AND", "OR", "IMP", "IFF"}:
            return LogicConnective(name, from_json(left), from_json(right))

        # Handling LogicQuantifiers
        case {"type": "LogicQuantifier", "name": "FORALL", "args": [v, formula]}:
            variable = from_json(v)
            if not isinstance(variable, Variable):
                raise ValueError(f"Invalid variable in FORALL quantifier: {v}")
            return LogicQuantifier("FORALL", variable, from_json(formula))

        case {"type": "LogicQuantifier", "name": "EXISTS", "args": [v, formula]}:
            variable = from_json(v)
            if not isinstance(variable, Variable):
                raise ValueError(f"Invalid variable in EXISTS quantifier: {v}")
            return LogicQuantifier("EXISTS", variable, from_json(formula))

        # Unknown type in JSON
        case _:
            raise ValueError(f"Unrecognized JSON structure: {json_obj}")