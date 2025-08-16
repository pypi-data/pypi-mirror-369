# This file is placed in the Public Domain.


"timer tests"


import unittest


from nixt.timer import Timed


def echo(txt):
    print(txt)


class TestTimer(unittest.TestCase):

    def test_construct(self):
        tmd = Timed(30, echo)
        self.assertEqual(type(tmd), Timed)
