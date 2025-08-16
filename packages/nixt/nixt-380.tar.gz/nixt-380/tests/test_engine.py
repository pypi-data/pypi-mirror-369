# This file is placed in the Public Domain.


"engine"


import unittest


from nixt.engine import Engine


class TestEngine(unittest.TestCase):

    def testcomposite(self):
        eng = Engine()
        self.assertEqual(type(eng), Engine)
