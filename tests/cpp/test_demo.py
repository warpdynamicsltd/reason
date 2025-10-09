import unittest

from reason import cpp

class TestCppTemplate(unittest.TestCase):
    def test_add_function(self):
        result = cpp.add(4, 7)
        self.assertEqual(result, 11)
