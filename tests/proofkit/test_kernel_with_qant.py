import pytest
import unittest

from reason.core.language import Language
from reason.proofkit.derived.tautologies import *
from reason.proofkit.derived.qty_rules import *
from reason.proofkit.derived.qty_tau import *
from reason.proofkit.derived.transform import *
from reason.proofkit.kernel.proof import *
from reason.proofkit.kernel import Kernel

L = Language()

class TestKernelWithQuant(unittest.TestCase):
    def test_simple(self):
        BEGIN()
        r1 = tau.p_to_p(L(f"P(x)"))
        GEN(r1, "x")
        f = RETURN()
        self.assertEqual(f, L("∀x. P(x) → P(x)"))

    def test_context_const(self):
        L = Language()
        L.add_const("context_0")
        block = Block(
            ref=Ref([]),
            statements=[
                Axiom(
                    ref=Ref([0]),
                    label="LEM",
                    fofs=[L("P(context_0)")],
                    terms=[],
                    formula=L("P(context_0) or ~P(context_0)")
                ),
                Rule(
                    ref=Ref([1]),
                    label="CTV",
                    refs=[Ref([0])],
                    terms=[Const("context_0"), Variable("x")],
                    formula=L("P(x) or ~P(x)")
                )
            ],
            formula=L("P(x) or ~P(x)")
        )

        Kernel.prove_tautology(block)

        L = Language()
        BEGIN(L)

        c = get_context_const_name()
        r1 = tau.p_to_p(L(f"P({c})")) # P(context_0) -> P(context_0)
        r2 = CTV(r1, c, "x") # P(x) → P(x)

        f = RETURN()
        self.assertEqual(f, L(f"P(x) → P(x)"))

        L = Language()
        BEGIN(L)
        c = get_context_const_name()
        self.assertEqual(c, "context_0")
        with Context():
            r0 = ASM(L(f"P({c})"))
            r1 = ref() # P(c0) -> P(c0)

        r2 = CTV(r1, c, "z")
        f = RETURN()
        self.assertEqual(f, L(f"P(z) → P(z)"))

        L = Language()
        BEGIN(L)
        with Context():
            c = get_context_const_name()
            self.assertEqual(c, "context_1")
            with Context():
                r0 = ASM(L(f"P({c})"))
                r1 = ref()  # P(c1) -> P(c1)

            r2 = CTV(r1, c, "z")
        f = RETURN()
        self.assertEqual(f, L(f"P(z) → P(z)"))

        L = Language()
        BEGIN(L)
        with Context():
            with Context():
                c = get_context_const_name()
                self.assertEqual(c, "context_2")
                with Context():
                    r0 = ASM(L(f"P({c})"))

                    r1 = ref()  # P(c1) -> P(c1)
                r2 = CTV(r1, c, "z")

        f = RETURN()
        self.assertEqual(f, L(f"P(z) → P(z)"))

        L = Language()
        BEGIN(L)
        c = get_context_const_name()
        r1 = tau.p_to_p(L(f"P(x, {c})"))  # P(x, c0) -> P(x, c0)
        r2 = CTV(r1, c, "x")  # P(x, x) → P(x, x)
        f = RETURN()
        self.assertEqual(f, L("P(x, x) → P(x, x)"))

    def test_skolem_const(self):
        L = Language()
        BEGIN(L)
        with Context():
            r0 = ASM(L("∃x. P(x)"))
            sk = get_next_skolem_const_name()
            r1 = SKO(r0, sk) # P(sk)
            g = formula(r1)
            r2 = EXT(L("P(z)"), Const(sk), "z") # P(sk) -> ∃z. P(z)
            r3 = MOD(r2, r1)
            r4 = ref()

        f = RETURN()
        self.assertEqual(f, L("( ∃x. P(x) ) → ( ∃z. P(z) )"))

    def test_statements(self):
        L = Language()
        BEGIN(L)
        all_to_exist(L("P(x)"), "x")
        f = RETURN()
        self.assertEqual(f, L("( ∀x. P(x) ) → ( ∃x. P(x) )"))

        L = Language()
        BEGIN(L)
        all_over_imp(L("A"), L("B(x)"), "x")
        f = RETURN()
        self.assertEqual(f, L(" ( ∀x. A → B(x) ) → ( A → ( ∀x. B(x) ) )"))

        L = Language()
        BEGIN(L)
        exists_over_imp(L("A"), L("B(x)"), "x")
        f = RETURN()
        self.assertEqual(f, L(" ( ∀x. B(x) → A ) → ( ( ∃x. B(x) ) → A )"))

        L = Language()
        BEGIN(L)
        de_morgan_not_exists_to_all_not(L("P(x)"), "x")
        f = RETURN()
        self.assertEqual(f, L("~ ( ∃x. P(x) ) → ( ∀x. ~P(x) )"))

        L = Language()
        BEGIN(L)
        de_morgan_exists_not_to_not_all(L("P(x)"), "x")
        f = RETURN()
        self.assertEqual(f, L("( ∃x. ~P(x) ) → ~( ∀x. P(x) )"))


    def test_rules(self):
        L = Language()
        BEGIN(L)
        with Context():
            r1 = ASM(L("P(x) ⟷ Q(x)"))
            with Context():
                r2 = ASM(L("∀x. P(x)"))
                r3 = r_iff_all(r1, r2, "x")
                self.assertEqual(formula(r3), L("∀x. Q(x)"))

        f = RETURN()
        self.assertEqual(f, L("(P(x) ⟷ Q(x)) → ( (∀x. P(x)) → (∀x. Q(x)))"))
