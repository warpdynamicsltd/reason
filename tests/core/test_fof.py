import unittest

from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory_v1 import Theory_v1
from reason.printer import Printer

class TestFof(unittest.TestCase):
  def test_selection(self):
    reason_parser = Parser()
    vampire_prover = Vampire()
    printer = Printer(reason_parser.ogc)

    T = Theory_v1(parser=reason_parser, prover=vampire_prover)

    case_list = [
      [
        "A({x ∈ z: P(x)})",
        "∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ P(x))"
      ],
      [
        "A({x ∈ z ∩ y: P(x)})",
        "∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∩ y ∧ P(x))"
      ],
      [
        "∀z. A({x ∈ z: P(x)})",
        "∀z. ∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ P(x))"
      ],
      [
        "A({x ∈ z: ∃k. P(k, x)})",
        "∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ (∃k. P(k, x)))"
      ],
      [
        "A({x ∈ z: ∃k. P({n ∈ k: B(n)}, x)})",
        "∃u2. A(u2) ∧ (∀x. x ∈ u2 ⟷ x ∈ z ∧ (∃k. ∃u1. P(u1, x) ∧ (∀n. n ∈ u1 ⟷ n ∈ k ∧ B(n))))"
      ],
      [
        "A({x ∈ z: ∃k. P({n ∈ f(k): B(n)}, x)})",
        "∃u2. A(u2) ∧ (∀x. x ∈ u2 ⟷ x ∈ z ∧ (∃k. ∃u1. P(u1, x) ∧ (∀n. n ∈ u1 ⟷ n ∈ f(k) ∧ B(n))))"
      ],
      [
        "A({x ∈ f(z): P(x)})",
        "∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ f(z) ∧ P(x))"
      ],
      [
        "A({x ∈ f(a, b): P(x)})",
        "∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ f(a, b) ∧ P(x))"
      ],
      [
        "A({x ∈ z: P(x)}, {x ∈ z: Q(x)})",
        "∃u1. ∃u2. A(u1, u2) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ P(x)) ∧ (∀x. x ∈ u2 ⟷ x ∈ z ∧ Q(x))"
      ],
      [
        "A({x ∈ a: B(x, {t ∈ b: C(t)})})",
        "∃u2. A(u2) ∧ (∀x. x ∈ u2 ⟷ x ∈ a ∧ (∃u1. B(x, u1) ∧ (∀t. t ∈ u1 ⟷ t ∈ b ∧ C(t))))"
      ],
      [
        "A({x ∈ a: B(x, {t ∈ b: C(t)}) ∧ D(x, {t ∈ d: E(t)})})",
        "∃u3. A(u3) ∧ (∀x. x ∈ u3 ⟷ x ∈ a ∧ ((∃u1. B(x, u1) ∧ (∀t. t ∈ u1 ⟷ t ∈ b ∧ C(t))) ∧ (∃u2. D(x, u2) ∧ (∀t. t ∈ u2 ⟷ t ∈ d ∧ E(t)))))"
      ],
      [
        "A({x ∈ a: B(x, {t ∈ b: C(t)})}, {x ∈ c: D(x, {t ∈ d: E(t)})})",
        "∃u2. ∃u4. A(u2, u4) ∧ (∀x. x ∈ u2 ⟷ x ∈ a ∧ (∃u1. B(x, u1) ∧ (∀t. t ∈ u1 ⟷ t ∈ b ∧ C(t)))) ∧ (∀x. x ∈ u4 ⟷ x ∈ c ∧ (∃u3. D(x, u3) ∧ (∀t. t ∈ u3 ⟷ t ∈ d ∧ E(t))))"
      ],
      [
        "A({x ∈ z: P(x)}) ∧ B({x ∈ z: Q(x)})",
        "(∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ P(x))) ∧ (∃u2. B(u2) ∧ (∀x. x ∈ u2 ⟷ x ∈ z ∧ Q(x)))"
      ],
      [
        "∀z. A({x ∈ z: P(x)}) ∧ B({x ∈ z: Q(x)})",
        "∀z. (∃u1. A(u1) ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ P(x))) ∧ (∃u2. B(u2) ∧ (∀x. x ∈ u2 ⟷ x ∈ z ∧ Q(x)))"
      ],
      [
        "(∀k. (P(k) → Q(k))) → {x ∈ z: P(x)} ⊂ {x ∈ z: Q(x)}",
        "(∀k. P(k) → Q(k)) → (∃u1. ∃u2. u1 ⊂ u2 ∧ (∀x. x ∈ u1 ⟷ x ∈ z ∧ P(x)) ∧ (∀x. x ∈ u2 ⟷ x ∈ z ∧ Q(x)))"
      ],
    ]

    for text, expected_text in case_list:
      self.assertEqual(printer(T.compile(text)), expected_text)