import re
import os
import json
from glob import glob
from beartype import beartype
from typing import Tuple

from reason.core.fof import FormulaBuilder
from reason.core.fof_types import FirstOrderFormula, LogicConnective
from reason.parser.tree import AbstractSyntaxTree
from reason.parser.tptp import TPTPParser
# from reason.core.transform.explode_conj import explode_over_conjunctions
from reason.vampire.translator import to_fof
from reason.core.transform.base import closure, make_bound_variables_unique
from reason.core.transform.signature import formula_sha256, signature
from reason.tools.math.transform import utf8_to_varname
from reason.parser.tree.consts import *

from reason.printer import Printer


class Theory_v1:
    def __init__(self, parser, prover, inspect=True, cache_folder_path=None):
        self.parser = parser
        self.tptp_parser = TPTPParser()
        self.prover = prover
        self.printer = Printer(parser.ogc)
        # self.axioms = []
        self.consts = {}
        # self.formula_builder = FormulaBuilder(consts=self.consts)
        self.inspect = inspect
        self.reference_dict: dict[str, FirstOrderFormula] = {}
        self.reference_signatures = set()

        self.cache_folder_path = cache_folder_path
        if self.cache_folder_path is not None:
            os.makedirs(self.cache_folder_path, exist_ok=True)

    def absorb_cache(self):
        if self.cache_folder_path is not None:
            for path in glob(f"{self.cache_folder_path}/*.json"):
                # print(path)
                m = re.match(r"^.+/([0-9a-f]{64})\.json$", path)
                if m:
                    (sha256,) = m.groups()
                    res = self.check_cache_file_compatibility(sha256)
                    # print(sha256, res)

    def cache_proof(self, proof_obj) -> bool:
        if self.cache_folder_path is not None:
            if len(proof_obj["conclusions"]) == 1:
                filename = f"{proof_obj['conclusions'][0]['signature_sha256']}.json"
                with open(os.path.join(self.cache_folder_path, filename), "w") as f:
                    json.dump(proof_obj, f, indent=2)
                    return True

        return False

    @beartype
    def to_formula(self, ast: AbstractSyntaxTree) -> FirstOrderFormula:
        formula, _ = self.to_formula_and_required_axioms(ast)
        return formula

    @beartype
    def to_formula_and_required_axioms(
        self, ast: AbstractSyntaxTree
    ) -> Tuple[FirstOrderFormula, list[FirstOrderFormula]]:
        builder = FormulaBuilder(ast, consts=self.consts)
        formula = builder.formula
        if self.inspect and not builder.well_formed():
            raise RuntimeError(f"{formula.show()} is not well formed")
        return formula, builder.axioms

    def compile(self, text: str) -> FirstOrderFormula:
        return self.to_formula(self.parser(text))

    def compile_and_get_axioms(self, text: str) -> Tuple[FirstOrderFormula, list[FirstOrderFormula]]:
        return self.to_formula_and_required_axioms(self.parser(text))

    def add_const(self, c: str):
        self.consts[c] = f"c{utf8_to_varname(c)}"

    @beartype
    def add_formula(self, f: str | AbstractSyntaxTree | FirstOrderFormula, name=None, type="theorem"):
        if not isinstance(f, FirstOrderFormula):
            s = self.symbolise(f)
            formula = self.to_formula(s)
        else:
            formula = f

        # if type == "axiom":
        #     self.axioms.append(formula)

        sig = signature(formula)
        if sig not in self.reference_signatures:
            self.reference_signatures.add(sig)
            inner_name = f"key_{len(self.reference_dict) + 1}"
            self.reference_dict[inner_name] = (name, formula)
            self.prover.add_formula(formula, inner_name, type)

    @beartype
    def add_axiom(self, f: str | AbstractSyntaxTree | FirstOrderFormula, name=None):
        self.add_formula(f, name, type="axiom")

    @beartype
    def add_axioms(self, formulas: list[str | AbstractSyntaxTree | FirstOrderFormula]):
        for formula in formulas:
            self.add_axiom(formula)

    @beartype
    def __call__(self, f: str | AbstractSyntaxTree | FirstOrderFormula) -> bool:
        if not isinstance(f, FirstOrderFormula):
            s = self.symbolise(f)
            s = self.to_formula(s)
            return self.prover(s)
        else:
            return self.prover(f)

    @beartype
    def symbolise(self, f: str | AbstractSyntaxTree) -> AbstractSyntaxTree:
        if not isinstance(f, AbstractSyntaxTree):
            return self.parser(f)
        else:
            return f

    # @beartype
    # def check_proof(
    #     self,
    #     premise: str | AbstractSyntaxTree | None,
    #     thesis: str | AbstractSyntaxTree,
    #     proof: str | AbstractSyntaxTree,
    # ) -> bool:
    #     if premise is not None:
    #         premise = self.symbolise(premise)
    #     thesis = self.symbolise(thesis)
    #     proof = self.symbolise(proof)
    #
    #     if premise is not None:
    #         consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
    #     else:
    #         consequences = explode_over_conjunctions(proof) + [thesis]
    #
    #     res = True
    #     for source, target in zip(consequences[:-1], consequences[1:]):
    #         source_formula, axioms = self.to_formula_and_required_axioms(source)
    #         self.add_axioms(axioms)
    #         target_formula, axioms = self.to_formula_and_required_axioms(target)
    #         self.add_axioms(axioms)
    #         f = LogicConnective(IMP, source_formula, target_formula)
    #         proof_obj = self.prove(f)
    #         print(self.printer(target_formula))
    #         if proof_obj is None:
    #             res = False
    #             break
    #
    #     return res
    #
    # @beartype
    # def add_lemmas(
    #     self, premise: str | AbstractSyntaxTree, thesis: str | AbstractSyntaxTree, proof: str | AbstractSyntaxTree
    # ) -> bool:
    #     premise = self.symbolise(premise)
    #     thesis = self.symbolise(thesis)
    #     proof = self.symbolise(proof)
    #
    #     if self.check_proof(premise, thesis, proof):
    #         consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
    #         for source, target in zip(consequences[:-1], consequences[1:]):
    #             formula = AbstractSyntaxTree(IMP, source, target)
    #             self.add_formula(formula, name=f"lemma{id(formula)}", type="theorem")
    #         return True
    #
    #     return False

    def parse_proof_line(self, line: str) -> str | None:
        re.match(r"^\d+\.(.*)\[input\(axiom|assumption\)\s(\w+)\]", line)

    def check_cache_premises_compatibility(self, cache_obj, premis_signatures: set):
        for premis in cache_obj["premises"]:
            f = self.tptp_parser(premis["formula"])
            sig = signature(f)
            if sig not in premis_signatures:
                proof_obj = self.prove(f)
                if proof_obj is None:
                    return False
                else:
                    self.add_formula(f, type="theorem")
                return False
        return True

    def check_cache_file_compatibility(self, sha256, formula: FirstOrderFormula | None = None):
        filename = f"{sha256}.json"
        path = os.path.join(self.cache_folder_path, filename)
        if os.path.exists(path):
            with open(path) as f:
                proof_obj = json.load(f)

            if proof_obj["proved"] and len(proof_obj["conclusions"]) == 1:
                read_formula = self.tptp_parser(proof_obj["conclusions"][0]["formula"])
                if formula is None:
                    self.add_formula(read_formula, type="theorem")
                if (
                    formula is None or signature(formula) == signature(read_formula)
                ) and self.check_cache_premises_compatibility(proof_obj, self.reference_signatures):
                    return proof_obj

        return None

    def check_if_proof_is_cached(self, formula: FirstOrderFormula) -> dict | None:
        if self.cache_folder_path is None:
            return None

        sha256 = formula_sha256(formula)
        return self.check_cache_file_compatibility(sha256, formula)

    def prove(self, formula: str | FirstOrderFormula) -> dict | None:
        if type(formula) is str:
            formula, new_axioms = self.compile_and_get_axioms(formula)
            self.add_axioms(new_axioms)

        proof_obj = self.check_if_proof_is_cached(formula)
        if proof_obj is not None:
            return proof_obj

        res = self.prover.run(formula, output_axiom_names="on")
        premises = []
        conclusions = []
        proof = []
        proved = False
        for line in res.split("\n"):
            match_line = re.match(r"^(\d+)\.\s(.*)\s\[(.*)\]$", line)
            if match_line:
                number, fof_formula, rule = match_line.groups()

                match_rule = re.match(r"^(.*)\s(\d+(?:,\d+)*)$", rule)
                if match_rule:
                    rule, sequence_str = match_rule.groups()
                    sequence = list(map(int, sequence_str.split(",")))
                else:
                    sequence = []

                proof.append({"id": int(number), "formula": fof_formula, "rule": rule, "sequence": sequence})

                match_input_comment = re.match(r"^input\((\w+)\)\s(\w+)$", rule)
                # print(line)
                if match_input_comment:
                    _type, reference_key = match_input_comment.groups()

                    if reference_key in self.reference_dict:
                        name, f = self.reference_dict[reference_key]
                    elif reference_key == "formula":
                        name = None
                        f = formula
                    else:
                        name = None
                        f = fof_formula

                    normalised_formula = make_bound_variables_unique(closure(f))

                    record = {
                        "metadata": {
                            "human_id": name,
                        },
                        "reference_id": reference_key,
                        "formula": to_fof(normalised_formula),
                        "signature_sha256": formula_sha256(f),
                    }

                    if _type in {"axiom", "assumption"}:
                        premises.append(record)

                    if _type == "conjecture":
                        conclusions.append(record)

        if proof[-1]["formula"] == "$false":
            proved = True

        if proved:
            proof_obj = {"proved": proved, "conclusions": conclusions, "premises": premises, "proof": proof}
            self.cache_proof(proof_obj)
            self.add_formula(formula, type="theorem")
            return proof_obj
        else:
            return None

    def provable(self, formula: str | FirstOrderFormula):
        proof_obj = self.prove(formula)
        return proof_obj is not None
