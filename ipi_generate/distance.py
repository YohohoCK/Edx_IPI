# coding=utf-8
# Author : How How, Yo Ho Ho

from collections import OrderedDict
from functools import reduce
from ngram import NGram
import math

nSize = 4


def norm(clickstream):
    if len(clickstream) < nSize:
        return 0
    n = NGram(N=nSize, pad_len=0, items=[clickstream])
    grams = n._grams
    vc = OrderedDict(zip(grams.keys(), [list(v.values())[0] for v in grams.values()]))
    return math.sqrt(reduce(lambda x, y: x + y * y, vc.values(), 0))


def cosw(pattern='1010',clickstream='',  vcnorm=1):
    if len(clickstream) < nSize:
        return 0
    return (clickstream.count(pattern)+0.0) / vcnorm


def lvw(s1='', s2='', w1=0.0, w2=1, w3=1):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
        w1, w2 = w2, w1
    distances = [i*w2 for i in range(len(s1) + 1)]
    for index2, char2 in enumerate(s2):
        newDistances = [w1*(index2+1)]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(min((distances[index1] + w3,
                                         distances[index1+1] + w1,
                                         newDistances[-1] + w2)))
        distances = newDistances
    return 1-distances[-1]
