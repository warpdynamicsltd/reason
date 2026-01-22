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
from reason.core.fof_types import FirstOrderFormula, Term
from reason.proofkit.kernel.proof import Ref, Axiom, Rule, Block
from reason.parser.ctxproof_tptp import CtxProofTPTPParser

DEBUG = False

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


class Kernel:
    @staticmethod
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