import unittest

from reason.core.language import Language
from reason.proofkit.derived.rules import *
from reason.proofkit.derived.tautologies import *
from reason.proofkit.derived.transform import *
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

    def test_derived_tautologies(self):
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
        r = de_morgan_not_and_to_or_not(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~(P ∧ Q) → ~P ∨ ~Q"))

        BEGIN()
        r = de_morgan_or_not_to_not_and(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~P ∨ ~Q → ~(P ∧ Q)"))

        BEGIN()
        de_morgan_not_or_to_and_not(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~(P ∨ Q) → ~P ∧ ~Q"))

        BEGIN()
        de_morgan_and_not_to_not_or(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~P ∧ ~Q → ~(P ∨ Q)"))

        BEGIN()
        r = de_morgan_not_or_to_and_not(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~(P ∨ Q) → ~P ∧ ~Q"))

        BEGIN()
        de_morgan_neg_con_iff_dis_neg(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~(P ∧ Q) ⟷ ~P ∨ ~Q"))

        BEGIN()
        de_morgan_neg_dis_iff_con_neg(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("~(P ∨ Q) ⟷ ~P ∧ ~Q"))

        BEGIN()
        r = p_to_p(L("P"))
        f = RETURN()
        self.assertEqual(f, L("P → P"))

        BEGIN()
        r = imp_inv(L("P"), L("Q"))
        f = RETURN()
        self.assertEqual(f, L("P → Q → (~Q → ~P)"))


        BEGIN()
        r = p_iff_not_not_p(L("P"))
        f = RETURN()
        self.assertEqual(f, L("P ⟷ ~~P"))

    def test_derived_rules(self):


        BEGIN()
        with Context():
            r0 = ASM(L("P → Q"))
            r1 = r_imp_to_dis(r0)
            self.assertEqual(formula(r1), L("~P ∨ Q"))

        with Context():
            r0 = ASM(L("A ⟷ B"))
            with Context():
                r1 = ASM(L("A ∨ C"))
                r2 = r_iff_or_left(r0, r1)
                self.assertEqual(formula(r2), L("B ∨ C"))

        # r_and_left, r_and_right
        with Context():
            r_and_ab = ASM(L("A ∧ B"))
            self.assertEqual(formula(r_and_left(r_and_ab)), L("A"))

        with Context():
            r_and_ab = ASM(L("A ∧ B"))
            self.assertEqual(formula(r_and_right(r_and_ab)), L("B"))

        # r_and
        with Context():
            ra = ASM(L("A"))
        with Context():
            rb = ASM(L("B"))
        r_and_ab2 = r_and(ra, rb)
        self.assertEqual(formula(r_and_ab2), L("A ∧ B"))

        # r_or_left
        with Context():
            ra = ASM(L("A"))
            r_or_ac = r_or_left(ra, L("C"))
            self.assertEqual(formula(r_or_ac), L("A ∨ C"))

        # r_or_right
        with Context():
            rb = ASM(L("B"))
            r_or_cb = r_or_right(L("C"), rb)
            self.assertEqual(formula(r_or_cb), L("C ∨ B"))

        # r_join_cases
        with Context():
            r_a_to_c = ASM(L("A → C"))
            with Context():
                r_b_to_c = ASM(L("B → C"))
                r_c = r_join_cases(r_a_to_c, r_b_to_c)

                self.assertEqual(formula(r_c), L("A ∨ B → C"))

        # r_join_exclusive_cases
        with Context():
            r_a_to_c = ASM(L("A → C"))
            with Context():
                r_b_to_d = ASM(L("~A → C"))
                r_c = r_join_exclusive_cases(r_a_to_c, r_b_to_d)
                self.assertEqual(formula(r_c), L("C"))

        # r_contradiction (explosion)
        with Context():
            r_a = ASM(L("A"))
            with Context():
                r_not_a = ASM(L("~A"))
                r_any = r_contradiction(r_a, r_not_a, L("B"))
                self.assertEqual(formula(r_any), L("B"))

        # r_imp_imp_iff
        with Context():
            r_a_iff_b = ASM(L("A → B"))
            with Context():
                r_b_imp_a = ASM(L("B → A"))
                r_iff = r_imp_imp_iff(r_a_iff_b, r_b_imp_a)
                self.assertEqual(formula(r_iff), L("A ⟷ B"))

        # r_imp_trans
        with Context():
            r_a_iff_b = ASM(L("A → B"))
            with Context():
                r_b_iff_c = ASM(L("B → C"))
                r_a_iff_c = r_imp_trans(r_a_iff_b, r_b_iff_c)
                self.assertEqual(formula(r_a_iff_c), L("A → C"))

        # r_iff_trans
        with Context():
            r_a_iff_b = ASM(L("A ⟷ B"))
            with Context():
                r_b_iff_c = ASM(L("B ⟷ C"))
                r_a_iff_c = r_iff_trans(r_a_iff_b, r_b_iff_c)
                self.assertEqual(formula(r_a_iff_c), L("A ⟷ C"))


        # r_iff_revolve
        with Context():
            r_ab = ASM(L("A ⟷ B"))
            r_ba = r_iff_revolve(r_ab)
            self.assertEqual(formula(r_ba), L("B ⟷ A"))

        # r_iff_imp
        with Context():
            r_ab = ASM(L("A ⟷ B"))
            with Context():
                r_a = ASM(L("A"))
                r_b = r_iff_imp(r_ab)
                self.assertEqual(formula(r_b), L("A → B"))

        # r_iff_imp_not
        with Context():
            r_ab = ASM(L("A ⟷ B"))
            r_not_b = r_iff_imp_not(r_ab)
            self.assertEqual(formula(r_not_b), L("~A → ~B"))

        # r_iff_mod
        with Context():
            r_ab = ASM(L("A ⟷ B"))
            with Context():
                r_a = ASM(L("A"))
                r_b = r_iff_mod(r_ab, r_a)
                self.assertEqual(formula(r_b), L("B"))

        # r_iff_mod_not
        with Context():
            r_ab = ASM(L("A ⟷ B"))
            with Context():
                r_not_a = ASM(L("~A"))
                r_not_b = r_iff_mod_not(r_ab, r_not_a)
                self.assertEqual(formula(r_not_b), L("~B"))

        # r_iff_or_right
        with Context():
            r0 = ASM(L("A ⟷ B"))
            with Context():
                r1 = ASM(L("C ∨ A"))
                r2 = r_iff_or_right(r0, r1)
                self.assertEqual(formula(r2), L("C ∨ B"))

        # r_to_not_not
        with Context():
            r_a = ASM(L("A"))
            r_nn_a = r_to_not_not(r_a)
            self.assertEqual(formula(r_nn_a), L("~~A"))

        # r_not_not_to
        with Context():
            r_nn_a = ASM(L("~~A"))
            r_a = r_not_not_to(r_nn_a)
            self.assertEqual(formula(r_a), L("A"))

        # r_proof_p_by_not_p
        with Context():
            r_not_a_implies_tau = ASM(L("~A → A"))
            r_a_from_pbn = r_proof_p_by_not_p(r_not_a_implies_tau)
            self.assertEqual(formula(r_a_from_pbn), L("A"))

        # r_inv_imp (contrapositive)
        with Context():
            r_a_iff_b = ASM(L("A → B"))
            r_contra = r_inv_imp(r_a_iff_b)
            self.assertEqual(formula(r_contra), L("~B → ~A"))

        # De Morgan variants
        with Context():
            r_neg_con = ASM(L("~(A ∧ B)"))
            r_dis_neg = r_de_morgan_neg_con(r_neg_con)
            self.assertEqual(formula(r_dis_neg), L("~A ∨ ~B"))

        with Context():
            r_dis_neg = ASM(L("~A ∨ ~B"))
            r_neg_con = r_de_morgan_dis_neg(r_dis_neg)
            self.assertEqual(formula(r_neg_con), L("~(A ∧ B)"))

        with Context():
            r_neg_dis = ASM(L("~(A ∨ B)"))
            r_con_neg = r_de_morgan_neg_dis(r_neg_dis)
            self.assertEqual(formula(r_con_neg), L("~A ∧ ~B"))

        with Context():
            r_con_neg = ASM(L("~A ∧ ~B"))
            r_neg_dis = r_de_morgan_con_neg(r_con_neg)
            self.assertEqual(formula(r_neg_dis), L("~(A ∨ B)"))

        # r_dis_com: A ∨ B |- B ∨ A
        with Context():
            r_dis = ASM(L("A ∨ B"))
            r_swapped = r_dis_com(r_dis)
            self.assertEqual(formula(r_swapped), L("B ∨ A"))

        with Context():
            r_con = ASM(L("A ∧ B"))
            r_swapped = r_con_com(r_con)
            self.assertEqual(formula(r_swapped), L("B ∧ A"))

        with Context():
            r1 = ASM(L("A ⟷ C"))
            with Context():
                r2 = ASM(L("A ∧ B"))
                r = r_iff_and_left(r1, r2)
                self.assertEqual(formula(r), L("C ∧ B"))

        with Context():
            r1 = ASM(L("A ⟷ C"))
            r = t_iff_and_left(r1, L("B"))
            self.assertEqual(formula(r), L("A ∧ B ⟷ C ∧ B"))


        f = RETURN()
