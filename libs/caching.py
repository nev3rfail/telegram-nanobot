# -*- coding: utf-8 -*-
# encoding=utf8

from collections import namedtuple
import time

class Pool:
    def __init__(self, update_function=None, ttl=36000):
        self.update_function = update_function
        self.ttl = ttl
        self.in_progress = False
        storeunit = namedtuple("item", "data created")
        self.pool = storeunit(data={}, created=0)


    def get_data(self):
        now = int(time.time())
        refill = False
        if now > self.pool.created + self.ttl:
            print("TTL reached, refill required.")
            refill = True

        if refill and not self.in_progress:
            self.in_progress = True
            newdata = self.update_function()
            if newdata:
                self.pool = self.pool._replace(data=newdata, created=int(time.time()))
            self.in_progress = False

        return self.pool.data
