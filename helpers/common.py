#!/usr/bin/env python2
#encoding: UTF-8

def replace_multiple(what, where, real_where=False):
    #todo: rewrite with regex

    #we got two lists here, with keys and with values
    if type(where) is list and type(real_where) is str:
        to = where
        where = real_where
        del real_where

        for index, lwhat in enumarate(what):
            if len(to) >= index and to[index] != False:
                where = where.replace(lwhat, to[index])
            else:
                where = where.replace(lwhat, '')

    elif type(what) is dict:
        for i, j in what.items():
            where = where.replace(i, j)
    elif type(what) is list:
        for _from, to in what:
            where = where.replace(_from, to)
    return where

