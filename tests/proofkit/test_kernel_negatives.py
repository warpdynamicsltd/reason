import pytest
import unittest

from reason.core.language import Language
import reason.proofkit.derived.rules as rules
import reason.proofkit.derived.tautologies as tau
from reason.proofkit.derived.qty_tau import *
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
            with pytest.raises(KernelError):
                Kernel.prove_tautology(proof_block)

    def test_context_negatives(self):
        L = Language()
        L.add_const("context_1")
        block = Block(
            ref=Ref([]),
            statements=[
                Axiom(
                    ref=Ref([0]),
                    label="LEM",
                    fofs=[L("P(context_1)")],
                    terms=[],
                    formula=L("P(context_1) or ~P(context_1)")
                ),
                # even if we do not check if context_1 is valid for Axiom with Ref([0])
                # check for CTV rule will cause KernelError
                Rule(
                    ref=Ref([1]),
                    label="CTV",
                    refs=[Ref([0])],
                    terms=[Const("context_1"), Variable("x")],
                    formula=L("P(x) or ~P(x)")
                )
            ],
            formula=L("P(x) or ~P(x)")
        )
        with pytest.raises(KernelError):
            Kernel.prove_tautology(block)

    def test_negatives_programs(self):
        L = Language()
        BEGIN(L)
        L.add_const("context_1")
        r = LEM(L("P(context_1)"))
        # print(r)
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)
        L.add_const("context_2")
        r = LEM(L("P(context_2)"))
        # print(r)
        with pytest.raises(KernelError):
            RETURN()


        L = Language()
        BEGIN(L)
        with Context():
            L.add_const("context_2")
            LEM(L("P(context_2)"))
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)
        with Context():
            c = get_context_const_name()
            LEM(L(f"P({c})"))
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)
        with Context():
            c = get_context_const_name()
            ASM(L(f"P({c})"))
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)
        c = get_context_const_name()
        r1 = tau.p_to_p(L(f"P(x, {c})"))  # P(x, c0) -> P(x, c0)
        r2 = CTV(r1, c, "x")  # P(x, x) → P(x, x)
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)

        with pytest.raises(RuntimeError):
            all_over_imp(L("A(x)"), L("B(x)"), "x")


        L = Language()
        BEGIN(L)
        with Context():
            c = get_context_const_name()
            with Context():
                r1 = ASM(L(f"P({c})")) # P(c)
                CTV(r1, c, "x") # ∀x. P(x)
                r2 = ref() # P(c) -> (∀x. P(x))
            CTV(r2, c, "z") # P(z) -> (∀x. P(x))
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)
        c = get_context_const_name()
        with Context():
            r1 = ASM(L(f"P({c})"))  # P(c)
            CTV(r1, c, "x")  # ∀x. P(x)
            r2 = ref()  # P(c) -> (∀x. P(x))
        CTV(r2, c, "z")  # P(z) -> (∀x. P(x))
        with pytest.raises(KernelError):
            RETURN()

        L = Language()
        BEGIN(L)
        c = get_context_const_name()
        with Context():
            with Context():
                r1 = ASM(L(f"P({c})"))  # P(c)
                CTV(r1, c, "x")  # ∀x. P(x)
                r2 = ref()  # P(c) -> (∀x. P(x))
            r3 = ref()
        CTV(r3, c, "z")  # P(z) -> (∀x. P(x))
        with pytest.raises(KernelError):
            RETURN()



