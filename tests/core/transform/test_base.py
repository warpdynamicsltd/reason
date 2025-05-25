import unittest
from collections import deque

from reason.core.fof_types import LogicConnective
from reason.core.fof_types import Variable
from reason.core.theory_v1 import Theory_v1
from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.transform.skolem import prenex_normal_raw, prenex_normal, skolem
from reason.core.transform.base import UniqueVariables, expand_iff, quantifier_signature, prepend_quantifier_signature, \
    invert_quantifier_signature, free_variables

class TestBase(unittest.TestCase):
    def test_free_variables(self):
        parser = Parser()
        vampire_prover = Vampire()

        T = Theory_v1(parser, vampire_prover)

        self.assertEqual(free_variables(T.compile("∀u. A(x, u) → (B(o) → (U(z)))")),
                         {Variable('x'), Variable('o'), Variable('z')})
        self.assertEqual(free_variables(T.compile("∀u. A(x, u) → (B(o) → (∃z. U(z)))")),
                         {Variable('x'), Variable('o')})
        self.assertEqual(free_variables(T.compile("∀u. A(u)")), set())
        self.assertEqual(free_variables(T.compile("A(u)")), {Variable('u')})