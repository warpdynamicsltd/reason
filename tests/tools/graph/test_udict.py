import unittest
from reason.tools.graph.iso_fun import isomorphic_dicts

class TestTree(unittest.TestCase):
    def test_few_dict(self):
        assert not isomorphic_dicts({0: 'a', 1: 'b', 2: 'c', 3: 'd'}, {0: 'a', 1: 'b', 2: 'c'})
        assert isomorphic_dicts({0: 'a', 1: 'b', 2: 'c', 3: 'd'}, {0: 'a', 1: 'b', 2: 'c', 3: 'd'})
        assert isomorphic_dicts({0: 'a', 1: 'a', 2: 'c', 3: 'd'}, {0: 'x', 1: 'x', 2: 'c', 3: 'd'})
        assert not isomorphic_dicts({0: 'a', 1: 's', 2: 'c', 3: 'd'}, {0: 'x', 1: 'x', 2: 'c', 3: 'd'})
        assert not isomorphic_dicts({0: 'a', 1: 'a', 2: 'c', 3: 'd'}, {0: 'x', 1: 's', 2: 'c', 3: 'd'})
        assert isomorphic_dicts({0: 'a', 1: 'a', 2: 'c', 3: 'd'}, {0: 'x', 1: 'x', 2: 'c', 3: 'e'})