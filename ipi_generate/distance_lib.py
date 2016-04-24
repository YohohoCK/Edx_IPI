# coding=utf-8
# Author : How How, Yo Ho Ho

from functools import reduce
from ngram import NGram
import math

nSize = 4


# Compute the norm of the clickstream vector
def norm(clickstream):
    n = NGram(N=nSize, pad_len=0, items=[clickstream])
    grams = n._grams
    vc = [list(v.values())[0] for v in grams.values()]
    return math.sqrt(reduce(lambda x, y: x + y * y, vc, 0))


# Compute the cosine weight of the clickstream with the pattern
def cos_wt(pattern='1010', clickstream='',  vcnorm=1):
    if vcnorm == 0:
        return 0
    return clickstream.count(pattern) / vcnorm


# Compute the Levenshtein weight of the clickstream with the pattern and fixed weight
def lv_dis(s1='', s2='', w1=0.0, w2=1, w3=1):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
        w1, w2 = w2, w1
    if s1 == s2:
        return 0
    distances = [i*w2 for i in range(len(s1) + 1)]
    for index2, char2 in enumerate(s2, 1):
        newDistances = [w1*index2]
        for index1, char1 in enumerate(s1, 1):
            if char1 == char2:
                newDistances.append(distances[index1-1])
            else:
                newDistances.append(min((distances[index1] + w1,
                                         newDistances[-1] + w2,
                                         distances[index1-1] + w3)))
        distances = newDistances
    return distances[-1]
