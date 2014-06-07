# -*- encoding: utf-8 -*-
from __future__ import print_function
import socket
import sys
import threading
import traceback


class OscListener(threading.Thread):
    r'''An OSC listener
    '''

    ### INITIALIZER ###

    def __init__(self, socket_instance, timeout=1):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._callbacks = {}
        self._running = False
        self._socket_instance = socket_instance
        self._timeout = int(timeout)

    ### PUBLIC PROPERTIES ###

    @property
    def callbacks(self):
        return self._callbacks

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, expr):
        self._running = bool(expr)

    @property
    def socket_instance(self):
        return self._socket_instance

    @property
    def timeout(self):
        return self._timeout

    ### PUBLIC METHODS ###

    def get_message(self):
        from supriya.library import osclib
        try:
            data, address = self.socket_instance.recvfrom(2**13)
            if data:
                message = osclib.OscMessage.from_datagram(data)
                return message
            return None
        except socket.timeout:
            return None

    def quit(self, wait=False):
        self._running = False
        if wait:
            self.join(2)

    def register_callback(self, key, callback):
        if not key in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)

    def run(self):
        self.running = True
        self.socket_instance.settimeout(0.5)
        try:
            while self.running:
                message = self.get_message()
                if message is None:
                    continue
                key = message.address
                callbacks = []
                callbacks += self.callbacks.get(None, [])
                callbacks += self.callbacks.get(key, [])
                for callback in callbacks:
                    callback(message)
        except:
            sys.stderr.write('Exception in listener thread:\n')
            traceback.print_exc()

    def unregister_callback(self, key, callback):
        if key in self.callbacks:
            if callback in self.callbacks[key]:
                self.callbacks[key].remove(callback)
                if not self.callbacks[key]:
                    del(self.callbacks[key])