# This file is placed in the Public Domain.


"event"


import threading
import time
import _thread


from .auto import Auto


class Event(Auto):

    def __init__(self):
        Auto.__init__(self)
        self._ready = threading.Event()
        self._thr = None
        self.ctime = time.time()
        self.result = {}
        self.type = "event"

    def done(self):
        self.reply("ok")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        try:
            self._ready.wait()
            if self._thr:
                self._thr.join()
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


def __dir__():
    return (
        'Event',
    )
