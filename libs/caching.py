# -*- coding: utf-8 -*-
# encoding=utf8

from collections import namedtuple
import re
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

class MultiPool:

    def __init__(self, update_function=None, ttl=36000):
        self.update_function = update_function
        self.ttl = ttl
        self.pool = {}
        self.in_progress = []
        self.storeunit = namedtuple("item", "data created")
        '''
        pool format is url => ['data' => [], 'created' => int]
        '''

    def get_key(self, url):
        return re.sub("&after=(.*)$", "", re.sub("\?after=(.*)$", "", url))


    def get_data(self, url, moar=False):
        now = int(time.time())
        key = self.get_key(url)
        print("\nKey is", key)
        if key not in self.pool:
            print("Key not in pool, fillinng it.")
            self.refill(url)
            return self.pool[key].data

        refill = False

        if self.pool[key].created > 0 and now > self.pool[key].created + self.ttl:
            print("TTL revalidation, cache+" + str(self.ttl) + " is older than now for a", now-self.pool[key].created + self.ttl, "s.")
            refill = True
        if refill:
            self.refill(url)

        if not refill and moar:
            self.append(url)

        return self.pool[key].data

    def refill(self, url):
        if url not in self.in_progress:
            self.in_progress.append(url)
            print("Refilling cache from " + url + "...")
            key = self.get_key(url)
            if key not in self.pool:
                self.pool[key] = self.storeunit(data=[], created=0)
            self.pool[key] = self.pool[key]._replace(data=self.update_function(url), created=int(time.time()))
            self.in_progress.remove(url)
        else:
            print(url, "is already refilling.")

    def append(self, url):
        key = self.get_key(url)
        if key not in self.pool:
            return self.refill(url)
        #print self.pool[key]
        self.pool[key]._replace(data=self.pool[key].data.extend(self.update_function(url)), created=int(time.time()))
        #self.pool[key]['data'].extend(self.do_request(url))
        #self.pool[key]['data']['created'] = int(time.time())