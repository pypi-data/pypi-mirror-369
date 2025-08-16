# This file is placed in the Public Domain.


"method tests"


import unittest


from nixt.auto import Auto


class TestMethods(unittest.TestCase):

    def test_auto(self):
        obj = Auto()
        obj.a = "b"
        self.assertEqual(obj.a, "b")
