# This file is placed in the Public Domain.


"thread tests"


import unittest


from nixt.object import Object
from nixt.thread import name


class TestComposite(unittest.TestCase):

    def test_name(self):
        obj = Object()
        nme = name(obj)
        self.assertEqual(nme, "nixt.object.Object")
