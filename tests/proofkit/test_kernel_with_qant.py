import pytest
import unittest

from reason.core.language import Language
from reason.proofkit.derived.tautologies import *
from reason.proofkit.derived.qty_tau import *
from reason.proofkit.derived.transform import *
from reason.proofkit.kernel.proof import *

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

    def test_statements(self):
        L = Language()
        BEGIN(L)
        all_to_exist(L("P(x)"), "x")
        f = RETURN()
        self.assertEqual(f, L("( ∀x. P(x) ) → ( ∃x. P(x) )"))