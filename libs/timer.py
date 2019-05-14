#encoding: UTF-8

from threading import Event
from threading import Thread
class Timer(Thread):
    def __init__(self, every):
        Thread.__init__(self)
        self.every = int(every)
        self.stopped = Event()
        self.functions = []

    def run(self):
        while not self.stopped.wait(self.every):
            #print("tick")
            for func in self.functions:
                func()

            # call a function
    def stop(self):
        self.stopped.set()

    def add(self, func):
        self.functions.append(func)