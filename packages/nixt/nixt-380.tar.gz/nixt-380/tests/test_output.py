# This file is placed in the Public Domain.


"output tests"


import unittest


from nixt.output import Output


class TestComposite(unittest.TestCase):

    def testcomposite(self):
        out = Output()
        self.assertEqual(type(out), Output)
