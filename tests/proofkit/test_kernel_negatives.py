import unittest

from reason.core.language import Language
from reason.proofkit.derived.rules import r_and_left, r_and_right, r_and
import reason.proofkit.derived.tautologies as tau
from reason.proofkit.kernel.proof import *
from reason.proofkit.kernel import Kernel, KernelError

L = Language()


class TestKernelNegatives(unittest.TestCase):
    invalid_blocks = [
        Block(
            ref=Ref([0]),
            statements=[
                Assumption(
                    ref=Ref([0, 0]),
                    formula=L("P")
                ),
                Rule(
                    ref=Ref([0, 1]),
                    label="IDN",
                    refs=[Ref([0, 0])],
                    terms=[],
                    formula=L("P")
                )
            ],
            formula=L("P → P")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([1]),
                    formula=L("P")
                ),
                Rule(
                    ref=Ref([2]),
                    label="IDN",
                    refs=[Ref([1])],
                    terms=[],
                    formula=L("P")
                )
            ],
            formula=L("P → P")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Rule(
                    ref=Ref([1]),
                    label="IDN",
                    refs=[Ref([1])],
                    terms=[],
                    formula=L("P")
                )
            ],
            formula=L("P → P")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Rule(
                    ref=Ref([1]),
                    label="IDN",
                    refs=[Ref([0])],
                    terms=[],
                    formula=L("Q")
                )
            ],
            formula=L("P → Q")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Block(
                    ref=Ref([1]),
                    statements=[
                        Rule(
                            ref=Ref([1, 0]),
                            label="IDN",
                            refs=[Ref([0])],
                            terms=[],
                            formula=L("P")
                        ),
                        Assumption(
                            ref=Ref([1, 1]),
                            formula=L("Q")
                        ),


                    ],
                    formula=L("Q → P")
                )
            ],
            formula=L("P → (Q → P)")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Block(
                    ref=Ref([1]),
                    statements=[
                        Assumption(
                            ref=Ref([1, 0]),
                            formula=L("Q")
                        ),

                        Rule(
                            ref=Ref([1, 1]),
                            label="AAA",
                            refs=[Ref([0])],
                            terms=[],
                            formula=L("P")
                        )
                    ],
                    formula=L("Q → P")
                )
            ],
            formula=L("P → (Q → P)")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Block(
                    ref=Ref([1]),
                    statements=[
                        Assumption(
                            ref=Ref([1, 0]),
                            formula=L("Q")
                        ),
                        Rule(
                            ref=Ref([1, 1]),
                            label="IDN",
                            refs=[Ref([0])],
                            terms=[],
                            formula=L("Q")
                        )
                    ],
                    formula=L("Q → Q")
                )
            ],
            formula=L("P → (Q → Q)")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Block(
                    ref=Ref([1]),
                    statements=[
                        Assumption(
                            ref=Ref([1, 1]),
                            formula=L("Q")
                        ),

                        Rule(
                            ref=Ref([1, 2]),
                            label="IDN",
                            refs=[Ref([0])],
                            terms=[],
                            formula=L("P")
                        )
                    ],
                    formula=L("Q → P")
                )
            ],
            formula=L("P → (Q → P)")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Axiom(
                    ref=Ref([1]),
                    label="XXX",
                    fofs=[L("P")],
                    terms=[],
                    formula=L("P or ~P")
                ),
                Rule(
                    ref=Ref([2]),
                    label="IDN",
                    refs=[Ref([1])],
                    terms=[],
                    formula=L("P or ~P")
                )
            ],
            formula=L("P → P or ~P")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Assumption(
                    ref=Ref([0]),
                    formula=L("P")
                ),
                Axiom(
                    ref=Ref([1]),
                    label="LEM",
                    fofs=[L("P")],
                    terms=[],
                    formula=L("~P or P")
                ),
                Rule(
                    ref=Ref([2]),
                    label="IDN",
                    refs=[Ref([1])],
                    terms=[],
                    formula=L("~P or P")
                )
            ],
            formula=L("P → ~P or P")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Axiom(
                    ref=Ref([0]),
                    label="LEM",
                    fofs=[L("P")],
                    terms=[],
                    formula=L("P or ~P")
                ),
                Assumption(
                    ref=Ref([1]),
                    formula=L("P")
                ),
                Rule(
                    ref=Ref([2]),
                    label="IDN",
                    refs=[Ref([0])],
                    terms=[],
                    formula=L("P or ~P")
                )
            ],
            formula=L("P → P or ~P")
        ),
        Block(
            ref=Ref([]),
            statements=[
                Block(
                    ref=Ref([0]),
                    statements=[
                        Assumption(
                            ref=Ref([0, 0]),
                            formula=L("A")
                        ),
                        Rule(
                            ref=Ref([0, 1]),
                            label="IDN",
                            refs=[Ref([0, 0])],
                            terms=[],
                            formula=L("A")
                        )
                    ],
                    formula=L("A → A")
                ),
                Block(
                    ref=Ref([1]),
                    statements=[
                        Assumption(
                            ref=Ref([1, 0]),
                            formula=L("Q")
                        ),
                        Rule(
                            ref=Ref([1, 1]),
                            label="IDN",
                            refs=[Ref([0, 1])],
                            terms=[],
                            formula=L("A")
                        )
                    ],
                    formula=L("Q → A")
                )
            ],
            formula=L("Q → (Q → A)")
        )

    ]

    def test_kernel_negatives(self):
        for i, proof_block in enumerate(TestKernelNegatives.invalid_blocks):
            try:
                f = Kernel.prove_tautology(proof_block)
            except Exception as e:
                self.assertIs(type(e), KernelError)
                continue

            raise RuntimeError(f"Kernel is expected to fail in {i}={proof_block.to_json()}")

    def test_fail_on_RETURN(self):
        try:
            f = RETURN()
        except Exception as e:
            self.assertIs(type(e), KernelError)
            return

    def test_kernel_programs_negatives(self):
        L = Language()
        BEGIN(L)
        with Context():
            c = get_context_const_name()
            r1 = tau.p_to_p(L(f"P({c})"))

        self.test_fail_on_RETURN()

        L = Language()
        BEGIN(L)
        with Context():
            c = get_context_const_name()
            ASM(L(f"P({c})"))

        self.test_fail_on_RETURN()

        L = Language()
        BEGIN(L)

        c = get_context_const_name()
        r1 = tau.p_to_p(L(f"P(x, {c})"))  # P(x, c0) -> P(x, c0)
        r2 = CTV(r1, c, "x")  # P(x, x) → P(x, x)

        self.test_fail_on_RETURN()


