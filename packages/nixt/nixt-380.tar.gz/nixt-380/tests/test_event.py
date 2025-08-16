# This file is placed in the Public Domain.


"composite"


import unittest


from nixt.event import Event


class TestComposite(unittest.TestCase):

    def test_construct(self):
        evt = Event()
        self.assertEqual(type(evt), Event)
