# This file is placed in the Public Domain.


"logging. tests"


import unittest


from nixt.fleet import Fleet


class TestFleet(unittest.TestCase):

    def test_construct(self):
        flt = Fleet()
        self.assertEqual(type(flt), Fleet)
