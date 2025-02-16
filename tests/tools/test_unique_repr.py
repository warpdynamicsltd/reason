import unittest

from reason.tools.unique_repr import UniqueRepr

class TestTheory(unittest.TestCase):

    def test_merge_unique_sorted_lists(self):
        self.assertListEqual(UniqueRepr.merge_unique_sorted_lists([1, 2, 5, 7], [2, 3, 4, 8]),
                             [1, 2, 3, 4, 5, 7, 8])

        self.assertListEqual(UniqueRepr.merge_unique_sorted_lists([], [2, 3, 4, 8]),
                             [2, 3, 4, 8])

        self.assertListEqual(UniqueRepr.merge_unique_sorted_lists([1, 2, 5, 7], []),
                             [1, 2, 5, 7])

        self.assertListEqual(UniqueRepr.merge_unique_sorted_lists([], []),
                             [])

        self.assertListEqual(UniqueRepr.merge_unique_sorted_lists([1, 2, 5, 7, 9], [0, 2, 3, 4, 7, 8]),
                             [0, 1, 2, 3, 4, 5, 7, 8, 9])

    def test_unique_repr(self):
        p1 = UniqueRepr([2, 3, 4, 8]) + UniqueRepr([2, 3, 4])
        self.assertListEqual(p1.get_sorted(), [(2, 3, 4), (2, 3, 4, 8)])

        p2 = UniqueRepr([2, 3, 4, 8])
        self.assertListEqual((p1*p2).get_sorted(), [])

        p1 = UniqueRepr(1) + UniqueRepr([2, 3, 4, 8]) + UniqueRepr([2, 3, 4])
        self.assertListEqual(p1.get_sorted(), [(1,), (2, 3, 4), (2, 3, 4, 8)])
        self.assertListEqual((p1 * p2).get_sorted(), [(2, 3, 4, 8)])

        p1 = UniqueRepr([2, 3, 5, 8]) + UniqueRepr([2, 4, 8])
        p2 = UniqueRepr([2, 3]) + UniqueRepr([2, 4, 8])
        self.assertListEqual((p1 * p2).get_sorted(), [(2, 3, 4, 5, 8), (2, 3, 4, 8), (2, 3, 5, 8), (2, 4, 8) ])

