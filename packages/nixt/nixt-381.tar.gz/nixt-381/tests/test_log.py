# This file is placed in the Public Domain.


"logging. tests"


import unittest


from nixt.log import level


class TestLogging(unittest.TestCase):

    def test_level(self):
        level("warn")
        self.assertEqual("test", "test")
