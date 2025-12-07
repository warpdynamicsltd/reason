import json
import re
import hashlib
import os
from pathlib import Path
from inspect import signature, Parameter
from subprocess import CalledProcessError
from typing import get_type_hints
from importlib.resources import files

from reason.tools.binary import run_binary
from reason.proofkit.kernel.jsonize import jsonize
from reason.proofkit.kernel.from_json import from_json
from reason.core.fof_types import FirstOrderFormula, Term
from reason.proofkit.kernel.proof import Ref, Axiom, Rule, Block
from reason.parser.ctxproof_tptp import CtxProofTPTPParser

DEBUG = True

class KernelError(Exception):
    pass

def save_proof_to_file(prefix: str, ctxproof_str: str):
    """
    Save ctxproof string to a file named by its SHA256 hash.
    Files are saved in the 'proofs' directory relative to this module.
    """
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    proofs_dir = module_dir / "proofs" / prefix

    # Create the proofs directory if it doesn't exist
    proofs_dir.mkdir(exist_ok=True)

    # Calculate SHA256 hash of the ctxproof string
    hash_digest = hashlib.sha256(ctxproof_str.encode('utf-8')).hexdigest()

    # Create the file path
    proof_file = proofs_dir / f"{hash_digest}.ctxproof"

    # Save the proof to the file
    with open(proof_file, 'w') as f:
        f.write(ctxproof_str)

def run(input):
    bin_path = files("reason") / "assets" / "bin" / "kernel"
    return run_binary(str(bin_path), input)

def run_ctxproof(input):
    bin_path = files("reason") / "assets" / "bin" / "ctxproof"
    return run_binary(str(bin_path), input)


def extract_formula_from_ctxproof(ctxproof_str: str) -> str:
    """
    Extract the formula part from a ctxproof string.
    The formula is the part before the opening brace {...}.

    For example:
    - ". p_A(X)\n{...}" -> "p_A(X)"
    - ". $true => p_B(Y)\n{...}" -> "$true => p_B(Y)"
    """
    # Match everything before the first {, extract the part after the reference
    match = re.match(r'^[^\s]+\s+(.+?)\s*\n?\s*\{', ctxproof_str, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        raise ValueError("Could not extract formula from ctxproof string")


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
                if DEBUG:
                    print(input_json)
                res = run(input_json)
                if DEBUG:
                    print(res)
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
    # @staticmethod
    # @kernel_command("ToCnf")
    # def to_cnf(formula: FirstOrderFormula) -> FirstOrderFormula:
    #     pass
    #
    # @staticmethod
    # @kernel_command("ToNnf")
    # def to_nnf(formula: FirstOrderFormula) -> FirstOrderFormula:
    #     pass
    #
    # @staticmethod
    # @kernel_command("ToEnnf")
    # def to_ennf(formula: FirstOrderFormula) -> FirstOrderFormula:
    #     pass
    #
    # @staticmethod
    # @kernel_command("Skolemize")
    # def skolemize(formula: FirstOrderFormula) -> FirstOrderFormula:
    #     pass
    #
    # @staticmethod
    # @kernel_command("Print")
    # def echo(formula: FirstOrderFormula) -> FirstOrderFormula:
    #     pass
    #
    # @staticmethod
    # @kernel_command("IsSimpleAxiom")
    # def is_simple_axiom(formula: FirstOrderFormula) -> bool:
    #     pass
    #
    # @staticmethod
    # @kernel_command("Sub")
    # def substitute(var: str, replacement: Term, formula: FirstOrderFormula) -> FirstOrderFormula:
    #     pass

    @staticmethod
    #@kernel_command("KernelProof")
    def prove_tautology(block: Block) -> FirstOrderFormula:
        # Get the ctxproof representation
        ctxproof_str = block.to_ctxproof()

        try:
            # Verify the proof with ctxproof binary
            run_ctxproof(ctxproof_str)
        except CalledProcessError as e:
            if DEBUG:
                save_proof_to_file("incorrect", ctxproof_str)
            raise KernelError(e.stderr.strip())

        if DEBUG:
            save_proof_to_file("correct", ctxproof_str)

        formula_str = extract_formula_from_ctxproof(ctxproof_str)

        # Parse the formula with CtxProofTPTPParser
        parser = CtxProofTPTPParser()
        formula = parser(formula_str)

        return formula