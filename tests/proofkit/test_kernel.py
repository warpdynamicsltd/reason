import unittest

from reason.core.language import Language
from reason.proofkit.derived.rules import r_and_left, r_and_right, r_and
from reason.proofkit.derived.tautologies import iff_tau, not_not_p_to_p, p_to_not_not_p, de_morgan_not_and_to_or, \
    p_to_p, imp_inv, imp_trans
from reason.proofkit.kernel.proof import *

L = Language()


class TestKernel(unittest.TestCase):

    def test_simple(self):
        BEGIN()
        with Context():
            r1 = ASM(L("P"))  # P
            with Context():
                r2 = ASM(L("Q"))  # Q
                IDN(r1);  # P
                r3 = ref()
            assert formula(r3) == L("Q → P")
            r4 = ref()
        assert formula(r4) == L("P → (Q → P)")
        f = RETURN()
        self.assertEqual(f, L("P → (Q → P)"))

        BEGIN()
        with Context():
            r1 = ASM(L("P → (Q1 → Q2)"))
            with Context():
                r2 = ASM(L("P → Q1"))
                with Context():
                    r3 = ASM(L("P"))
                    r4 = MOD(r2, r3)
                    assert formula(r4) == L("Q1")
                    r5 = MOD(r1, r3)
                    assert formula(r5) == L("Q1 → Q2")
                    r6 = MOD(r5, r4)
                    assert formula(r6) == L("Q2")
                    r7 = ref()
                assert formula(r7) == L("P → Q2")
                r8 = ref()
            assert formula(r8) == L("(P → Q1) → (P → Q2)")
            r9 = ref()

        f = RETURN()
        self.assertEqual(f, L("P → (Q1 → Q2) → (P → Q1 → (P → Q2))"))

        BEGIN()
        with Context():
            r1 = ASM(L("(A → B) ∧ (B → C)"))
            r2 = ANL(L("A → B"), L("B → C"))
            r3 = MOD(r2, r1)
            assert formula(r3) == L("A → B")
            r4 = ANR(L("A → B"), L("B → C"))
            r5 = MOD(r4, r1)
            assert formula(r5) == L("B → C")
            with Context():
                r6 = ASM(L("A"))
                r7 = MOD(r3, r6)
                assert formula(r7) == L("B")
                r8 = MOD(r5, r7)
                assert formula(r8) == L("C")
                r9 = ref()
            assert formula(r9) == L("A → C")
            r10 = ref()

        f = RETURN()
        self.assertEqual(f, L("(A → B) ∧ (B → C) → (A → C)"))

        BEGIN()
        with Context():
            r1 = ASM(L("(A → B) ∧ (B → C)"))
            r3 = r_and_left(r1)
            assert formula(r3) == L("A → B")
            r5 = r_and_right(r1)
            assert formula(r5) == L("B → C")
            with Context():
                r6 = ASM(L("A"))
                r7 = MOD(r3, r6)
                assert formula(r7) == L("B")
                r8 = MOD(r5, r7)
                assert formula(r8) == L("C")
                r9 = ref()
            assert formula(r9) == L("A → C")
            r10 = ref()

        f = RETURN()
        self.assertEqual(f, L("(A → B) ∧ (B → C) → (A → C)"))

        BEGIN()
        with Context():
            r1 = ASM(L("(A → B) ∧ (B → A)"))
            r2 = IFI(L("A"), L("B"))
            assert formula(r2) == L(("(A → B) → ((B → A) → (A ⟷ B))"))
            r3 = r_and_left(r1)
            assert formula(r3) == L("A → B")
            r4 = r_and_right(r1)
            assert formula(r4) == L("B → A")
            r5 = MOD(r2, r3)
            assert formula(r5) == L("(B → A) → (A ⟷ B)")
            r6 = MOD(r5, r4)
            r10 = ref()

        f = RETURN()
        self.assertEqual(f, L("(A → B) ∧ (B → A) → (A ⟷ B)"))

    def test_derived(self):
        BEGIN()
        imp_trans(L("A"), L("B"), L("C"))
        f = RETURN()
        self.assertEqual(f, L("(A → B) ∧ (B → C) → (A → C)"))

        BEGIN()
        r1 = iff_tau(L("A"), L("B"))
        r2 = IFO(L("A"), L("B"))
        r3 = iff_tau(L("(A → B) ∧ (B → A)"), L("A ⟷ B"))
        r5 = r_and(r1, r2)
        MOD(r3, r5)
        f = RETURN()
        self.assertEqual(f, L("(A → B) ∧ (B → A) ⟷ (A ⟷ B)"))

        BEGIN()
        iff_tau(L("A"), L("B"))
        f = RETURN()
        self.assertEqual(f, L("(A → B) ∧ (B → A) → (A ⟷ B)"))

        BEGIN()
        r = not_not_p_to_p(L("P"))
        f = RETURN()
        self.assertEqual(f, L("~~P → P"))

        BEGIN()
        r = p_to_not_not_p(L("P"))
        f = RETURN()
        self.assertEqual(f, L("P → ~~P"))

        BEGIN()
        r = de_morgan_not_and_to_or(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~(P ∧ Q) → ~P ∨ ~Q"))

        BEGIN()
        r = p_to_p(L("P"))
        f = RETURN()
        self.assertEqual(f, L("P → P"))

        BEGIN()
        r = imp_inv(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("P → Q → (~Q → ~P)"))