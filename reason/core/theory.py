import re
from beartype import beartype

from reason.core.fof import FirstOrderFormula, FormulaBuilder, LogicConnective
from reason.parser.tree import AbstractSyntaxTree
from reason.core.transform.explode_conj import explode_over_conjunctions
from reason.vampire.translator import to_fof
from reason.core.transform.base import closure

from reason.printer import Printer


class Theory:
    def __init__(self, parser, prover, inspect=True):
        self.parser = parser
        self.prover = prover
        # self.axioms = []
        self.consts = {}
        self.formula_builder = FormulaBuilder(consts=self.consts)
        self.inspect = inspect
        self.reference_translator = {}

    @beartype
    def to_formula(self, ast: AbstractSyntaxTree) -> FirstOrderFormula:
        formula = self.formula_builder(ast)
        if self.inspect and not self.formula_builder.well_formed(formula):
            raise ValueError(f"{formula.show()} is not well formed")
        return formula

    def compile(self, text: str) -> FirstOrderFormula:
        return self.to_formula(self.parser(text))

    def add_const(self, c: str):
        self.consts[c] = f"c{len(self.consts)}"

    @beartype
    def add_formula(self, f: str | AbstractSyntaxTree, name, type):
        s = self.symbolise(f)
        formula = self.to_formula(s)
        # self.axioms.append(s)

        inner_name = f"key_{len(self.reference_translator) + 1}"

        self.reference_translator[inner_name] = (name, formula)

        self.prover.add_formula(formula, inner_name, type)

    @beartype
    def add_axiom(self, f: str | AbstractSyntaxTree, name):
        self.add_formula(f, name, type="axiom")

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

    @beartype
    def check_proof(
        self, premise: str | AbstractSyntaxTree, thesis: str | AbstractSyntaxTree, proof: str | AbstractSyntaxTree
    ) -> bool:
        premise = self.symbolise(premise)
        thesis = self.symbolise(thesis)
        proof = self.symbolise(proof)

        consequences = [premise] + explode_over_conjunctions(proof) + [thesis]

        printer = Printer(self.parser.ogc)

        res = True
        for source, target in zip(consequences[:-1], consequences[1:]):
            f = LogicConnective("IMP", self.to_formula(source), self.to_formula(target))
            # print(printer(f))
            if not self(f):
                res = False
                break

        return res

    @beartype
    def add_lemmas(
        self, premise: str | AbstractSyntaxTree, thesis: str | AbstractSyntaxTree, proof: str | AbstractSyntaxTree
    ) -> bool:
        premise = self.symbolise(premise)
        thesis = self.symbolise(thesis)
        proof = self.symbolise(proof)

        if self.check_proof(premise, thesis, proof):
            consequences = [premise] + explode_over_conjunctions(proof) + [thesis]
            for source, target in zip(consequences[:-1], consequences[1:]):
                formula = AbstractSyntaxTree("IMP", source, target)
                self.add_formula(formula, name=f"lemma{id(formula)}", type="theorem")
            return True

        return False

    def parse_proof_line(self, line: str) -> str | None:
        re.match(r"^\d+\.(.*)\[input\(axiom|assumption\)\s(\w+)\]", line)

    def prove(self, formula: FirstOrderFormula) -> dict | None:
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

                    if reference_key in self.reference_translator:
                        name, f = self.reference_translator[reference_key]
                    elif reference_key == "formula":
                        name = None
                        f = formula
                    else:
                        name = None
                        f = fof_formula

                    record = {
                        "metadata": {
                            "human_id": name,
                        },
                        "reference_id": reference_key,
                        "formula": to_fof(closure(f)),
                    }

                    if _type in {"axiom", "assumption"}:
                        premises.append(record)

                    if _type == "conjecture":
                        conclusions.append(record)

        if proof[-1]["formula"] == "$false":
            proved = True

        if proved:
            res = {"proved": proved, "conclusions": conclusions, "premises": premises, "proof": proof}
            return res
        else:
            return None
