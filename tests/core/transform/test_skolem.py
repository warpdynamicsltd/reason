import unittest
from collections import deque

from reason.core.fof_types import LogicConnective
from reason.core.fof_types import Variable
from reason.core.theory import Theory
from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.transform.skolem import prenex_normal_raw, prenex_normal, skolem, SkolemUniqueRepr, skolem_sha256
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    invert_quantifier_signature, closure


class TestSkolem(unittest.TestCase):
    def test_expand_iff(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)

        self.assertEqual(expand_iff(T.compile("(Q ⟷ R(x))")), T.compile("((Q → R(x)) ∧ (R(x) → Q))"))
        self.assertEqual(expand_iff(T.compile("P ∧ (Q ⟷ R)")), T.compile("P ∧ ((Q → R) ∧ (R → Q))"))
        self.assertEqual(expand_iff(T.compile("(Q ⟷ (∀x. R(x)))")), T.compile("((Q → (∀x. R(x))) ∧ ((∀x. R(x)) → Q))"))
        self.assertEqual(expand_iff(T.compile("(Q ⟷ (∀x. R ⟷ P))")), T.compile("((Q → (∀x. (R → P) ∧ (P → R))) ∧ ((∀x. (R → P) ∧ (P → R)) → Q))"))

    def test_quantifier_signature(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)
        f, signature = quantifier_signature(T.compile("∃u.∀x.∀y.∃z. P(x) → R(u, y, z)"))
        self.assertEqual(signature, deque([('EXISTS', Variable('u')), ('FORALL', Variable('x')), ('FORALL', Variable('y')), ('EXISTS', Variable('z'))]))
        self.assertEqual(f, T.compile("P(x) → R(u, y, z)"))

    def test_prepend_quantifier_signature(self):
        parser = Parser()
        vampire_prover = Vampire()
        T = Theory(parser, vampire_prover)
        f = T.compile("P(x) → R(u, y, z)")
        signature = [('EXISTS', Variable('u')), ('FORALL', Variable('x')), ('FORALL', Variable('y')), ('EXISTS', Variable('z'))]
        self.assertEqual(prepend_quantifier_signature(f, signature), T.compile("∃u.∀x.∀y.∃z. P(x) → R(u, y, z)"))

    def test_invert_quantifier_signature(self):
        signature = [('EXISTS', Variable('u')), ('FORALL', Variable('x')), ('FORALL', Variable('y')),
                     ('EXISTS', Variable('z'))]
        self.assertListEqual(invert_quantifier_signature(signature), [('FORALL', Variable('u')), ('EXISTS', Variable('x')), ('EXISTS', Variable('y')), ('FORALL', Variable('z'))])


    def test_prenex_normal(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)
        self.assertEqual(prenex_normal_raw(T.compile("~(∀x.∃u. P)")), T.compile("∃x.∀u. ~P"))
        self.assertEqual(prenex_normal_raw(T.compile("(∀x.∃u. A) ∧ (∃y.∀z. B)")), T.compile("∀x.∃u.∃y.∀z. A ∧ B"))
        self.assertEqual(prenex_normal_raw(T.compile("(∀x.∃u. A) ∧ ~(∃y.∀z. B)")), T.compile("∀x.∃u.∀y.∃z. A ∧ ~B"))
        self.assertEqual(prenex_normal_raw(T.compile("(∀x.∃u. A) ∨ (∃y.∀z. B)")), T.compile("∀x.∃u.∃y.∀z. A ∨ B"))

        self.assertEqual(prenex_normal_raw(T.compile("(∀x. A) → B")), T.compile("∃x. A → B"))
        self.assertEqual(prenex_normal_raw(T.compile("A → (∀x. B)")), T.compile("∀x. A → B"))

        self.assertEqual(prenex_normal_raw(T.compile("∃u. Q ∧ ((∃x. A) → (∀y. B))")), T.compile("∃u.∀x.∀y. Q ∧ (A → B)"))
        self.assertEqual(prenex_normal_raw(T.compile("∃u. Q ∧ ~((∃x. A) → (∀y. B))")), T.compile("∃u.∃x.∃y. Q ∧ ~(A → B)"))

        self.assertEqual(prenex_normal(T.compile("∃u. Q ∧ ~((∃x. A) → (∀y. B))")),
                         T.compile("∃x1.∃x2.∃x3. Q ∧ ~(A → B)"))

        self.assertEqual(prenex_normal(T.compile("(∀x. A(x)) ⟷ B")),
                         T.compile("∃x1.∀x2. (A(x1) → B) ∧ (B → A(x2))"))

        self.assertEqual(prenex_normal(T.compile("(∀x. A(x)) ⟷ (∃u. B(u))")),
                         T.compile("∃x1.∃x2.∀x3.∀x4. (A(x1) → B(x2)) ∧ (B(x3) → A(x4))"))


    def test_prenex_form_tautologies(self):
        texts = [
            "(∀x. A(x)) ⟷ (∃u. B(u))",
            "A ⟷ B",
            "(∀x. A(x)) ⟷ B",
            "A ⟷ (∀x. B(x))",
            "∃u. Q(u) ∧ ~((∃x. A(x)) → (∀y. B(y)))",
            "(∀x.∃u. A(x, u)) ∧ (∃y.∀z. B(y, z))",
            "(∀x.∃u. A(x, u)) ∨ (∃y.∀z. B(y, z))",
            "(∀x.∃u. A(x, u)) ∧ ~(∃y.∀z. B(y, z))"
        ]

        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)
        for text in texts:
            f = T.compile(text)

            tautology = LogicConnective('IFF', f, prenex_normal(f))

            # Formula is always logically equivalent to its prenex normal form
            # so f <-> prenex_normal(f) is a tautology
            self.assertTrue(T.prover(tautology))

    def test_skolem_tautologies(self):
        texts = [
            "(∀x. A(x)) ⟷ (∃u. B(u))",
            "A ⟷ B",
            "(∀x. A(x)) ⟷ B",
            "A ⟷ (∀x. B(x))",
            "∃u. Q(u) ∧ ~((∃x. A(x)) → (∀y. B(y)))",
            "(∀x.∃u. A(x, u)) ∧ (∃y.∀z. B(y, z))",
            "(∀x.∃u. A(x, u)) ∨ (∃y.∀z. B(y, z))",
            "(∀x.∃u. A(x, u)) ∧ ~(∃y.∀z. B(y, z))"
        ]

        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)
        for text in texts:
            f = T.compile(text)

            tautology = LogicConnective('IMP', closure(skolem(f)), f)
            self.assertTrue(T.prover(tautology))

    def test_unique_representation_tautologies(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory(parser, vampire_prover)

        truth = ((1,),)

        self.assertEqual(SkolemUniqueRepr(T.compile("P ∨ ~P")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("P → P")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("~(A ∧ B) ⟷ ~A ∨ ~B")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("~(A ∨ B) ⟷ ~A ∧ ~B")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("P → (Q → P ∧ Q)")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("P → (Q → P ∧ Q)")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("P → (Q → P ∨ Q)")).result, truth)
        self.assertEqual(SkolemUniqueRepr(T.compile("P ∧ Q → P")).result, truth)




