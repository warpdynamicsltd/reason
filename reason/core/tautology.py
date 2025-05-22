import re

from reason.core.fof_types import FirstOrderFormula
from reason.vampire import Vampire
from reason.vampire.translator import to_fof
from reason.core.transform.base import closure, make_bound_variables_unique
from reason.core.transform.signature import formula_sha256
from beartype import beartype


@beartype
def prove(conjucture: FirstOrderFormula, premises: list[FirstOrderFormula]) -> dict | None:
    prover = Vampire()
    reference_dict = {}
    for premis in premises:
        inner_name = f"key_{len(reference_dict) + 1}"
        reference_dict[inner_name] = premis
        prover.add_axiom(premis, name=inner_name)

    res = prover.run(conjucture, output_axiom_names="on")
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

                if reference_key in reference_dict:
                    f = reference_dict[reference_key]
                elif reference_key == "formula":
                    name = None
                    f = conjucture
                else:
                    name = None
                    f = fof_formula

                normalised_formula = make_bound_variables_unique(closure(f))

                record = {
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
        return proof_obj
    else:
        return None
