import json
from inspect import signature, Parameter
from subprocess import CalledProcessError
from typing import get_type_hints
from importlib.resources import files

from reason.tools.binary import run_binary
from reason.core.transform.jsonize import jsonize
from reason.core.transform.from_json import from_json
from reason.core.fof_types import FirstOrderFormula, Term
from reason.proofkit.kernel.proof import Ref, Axiom, Rule, Block


class KernelError(Exception):
    pass

def run(input):
    bin_path = files("reason") / "assets" / "bin" / "kernel"
    return run_binary(str(bin_path), input)


def kernel_command(command_name):
    """
    A decorator to dynamically serialize function arguments into JSON format
    suitable for sending to main.ml. Arguments are serialized differently
    based on their type annotations.

    :param command_name: The name of the kernel command being executed.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_signature = signature(func)
            type_hints = get_type_hints(func)

            serialized_args = []
            for i, (name, param) in enumerate(func_signature.parameters.items()):
                if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                    # Skip *args and **kwargs for now
                    continue

                # Determine the argument value (from args or kwargs)
                if name in kwargs:
                    value = kwargs[name]
                elif i < len(args):
                    value = args[i]
                else:
                    value = param.default

                # Serialize the argument using match-case
                match value:
                    case FirstOrderFormula():
                        serialized_args.append(jsonize(value))
                    case Term():
                        serialized_args.append(jsonize(value))
                    case Block():
                        serialized_args.append(value.to_json())
                    case _:
                        # Default serialization rule for unrecognized types
                        serialized_args.append(value)

            # Create the JSON payload
            payload = {
                "type": "Command",
                "name": command_name,
                "args": serialized_args
            }

            # Run the serialized input through Kernel run method
            input_json = json.dumps(payload)

            try:
                res = run(input_json)
            except CalledProcessError as e:
                raise KernelError(e.stderr.strip())

            response = json.loads(res)

            return_type = func_signature.return_annotation

            match return_type.__name__:
                case "Term":
                    return from_json(response)

                case "FirstOrderFormula":
                    return from_json(response)

                case "int":
                    if response["type"] == "Int":
                        return int(response["args"][0])
                    else:
                        raise RuntimeError("Unexpected return type")
                case "bool":
                    if response["type"] == "Bool":
                        return response["args"][0];
                    else:
                        raise RuntimeError("Unexpected return type")

                case _:
                    raise RuntimeError("Unknown return type")

        return wrapper

    return decorator



class Kernel:
    @staticmethod
    @kernel_command("ToCnf")
    def to_cnf(formula: FirstOrderFormula) -> FirstOrderFormula:
        pass

    @staticmethod
    @kernel_command("ToNnf")
    def to_nnf(formula: FirstOrderFormula) -> FirstOrderFormula:
        pass

    @staticmethod
    @kernel_command("ToEnnf")
    def to_ennf(formula: FirstOrderFormula) -> FirstOrderFormula:
        pass

    @staticmethod
    @kernel_command("Skolemize")
    def skolemize(formula: FirstOrderFormula) -> FirstOrderFormula:
        pass

    @staticmethod
    @kernel_command("Print")
    def echo(formula: FirstOrderFormula) -> FirstOrderFormula:
        pass

    @staticmethod
    @kernel_command("IsSimpleAxiom")
    def is_simple_axiom(formula: FirstOrderFormula) -> bool:
        pass

    @staticmethod
    @kernel_command("Sub")
    def substitute(var: str, replacement: Term, formula: FirstOrderFormula) -> FirstOrderFormula:
        pass

    @staticmethod
    @kernel_command("KernelProof")
    def prove_tautology(block: Block) -> FirstOrderFormula:
        pass