# This file is placed in the Public Domain.


"client"


import io
import threading
import unittest


from nixt.client import Client
from nixt.event  import Event
from nixt.fleet  import Fleet
from nixt.object import values


import nixt.client


class MockClient(Client):

    result = io.StringIO()

    def raw(self, txt):
        self.result.write(txt)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.clt = MockClient()

    def tearDown(self):
        self.clt.result = io.StringIO()

    def interface(self):
        self.assertTrue('Client', dir(nixt.client))

    def test_construct(self):
        clt = Client()
        self.assertEqual(type(clt), Client)
        self.assertEqual(type(clt.olock), type(threading.RLock()))
        self.assertTrue(clt in values(Fleet.clients))

    def test_announce(self):
        self.assertTrue(True)

    def test_display(self):
        evt = Event()
        evt.reply("test")
        self.clt.display(evt)
        print(self.clt.result)
        self.assertTrue("test" in self.clt.result.getvalue())

    def test_dosay(self):
        self.clt.dosay('#test', 'test')
        self.assertTrue("test" in self.clt.result.getvalue())

    def test_raw(self):
        self.clt.raw('test')
        self.assertTrue("test" in self.clt.result.getvalue())

    def test_say(self):
        self.clt.say('#test', 'test')
        self.assertTrue("test" in self.clt.result.getvalue())
