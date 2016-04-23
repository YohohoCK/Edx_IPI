# coding=utf-8
# Author : How How & Yo Ho Ho
from collections import OrderedDict
from collections import namedtuple
from ngram import NGram
from ipi import distance
import operator

""" Basic setting """
nSize = 4
pSize = 100
testNum = 1000

eventFileName = 'user_events.txt'
patternFileName = 'pattern.txt'
categoryFileName = 'category.txt'
ipiFileName = 'IPI_full.txt'
divider = '--------------------'
# Data type
View = namedtuple('View', ['username', 'module_id', 'duration', 'start_time', 'end_time', 'clickstream', 'non_dropout'])
Pattern = namedtuple('Pattern', ['string', 'num', 'times', 'count', 'non_dropout', 'dropout', 'rate'])
Clickstream = namedtuple('ClickStream', ['num', 'non_dropout'])
# Pattern in number form
symbol2num = OrderedDict([('Pl', '0'), ('Pa', '1'), ('SSf', '2'), ('SSb', '3'), ('Sf', '4'), ('Sb', '5'), ('St', '6')])
num2symbol = OrderedDict(zip(symbol2num.values(), symbol2num.keys()))
# Category parameter
cateDict = OrderedDict([('Clear_Concept', [0.40, 3]),
                        ('Rewatch', [0.3, 1]),
                        ('Checkback_Reference', [0.26, -1]),
                        ('Skipping', [0, -3])])
# data
views = []
clickstreams_num = []
patterns = []
categories = OrderedDict([])
weights = []
''' Define functions '''


# change clickstream's symbol to number form
def sym2num(cl):
    ans = cl
    for key in symbol2num.keys():
        ans = ans.replace(key, symbol2num[key])
    return ans


# change clickstream's symbol to number form
def num2sym(cl):
    ans = cl
    for key in num2symbol.keys():
        ans = ans.replace(key, num2symbol[key])
    return ans


# Read event file
def read_event():
    print('Reading event file...', end='')
    views.clear()
    with open(eventFileName, 'r') as file:
        for view in map(View._make, [line.split() for line in file.readlines()]):
            views.append(view)
    clickstreams_num.clear()
    for view in views:
        clickstreams_num.append(Clickstream(sym2num(view.clickstream), view.non_dropout))

    print('Complete')


# Find top 100 n-gram patterns
def find_patterns():
    print('Doing N-Gram...', end='')
    patterns_pre = {}
    for clickstream in clickstreams_num:
        n = NGram(N=nSize, pad_len=0, items=[clickstream.num])
        grams = n._grams
        grams2 = dict(zip(grams.keys(), [list(v.values())[0] for v in grams.values()]))
        for k in grams2.keys():
            if k in patterns_pre.keys():
                patterns_pre[k] += grams2[k]
            else:
                patterns_pre[k] = grams2[k]
    patterns_pre = sorted(patterns_pre.items(), key=operator.itemgetter(1), reverse=True)
    patterns_pre = patterns_pre[0:pSize if pSize <= len(patterns_pre) else len(patterns_pre)]
    print('Complete')
    return patterns_pre


# Analyze patterns' non-dropout rate
def analyze_patterns():
    patterns_pre = find_patterns()
    print('Analyzing patterns...', end='')
    patterns.clear()
    for num, times in patterns_pre:
        pattern = []
        symbols = [num2symbol[n] for n in num]
        pattern.append(''.join(symbols))
        pattern.append(num)
        pattern.append(times)
        non_dropout = 0
        dropout = 0
        for (clickstream, nd) in clickstreams_num:
            if num in clickstream:
                if nd == '1':
                    non_dropout += 1
                else:
                    dropout += 1
        pattern.append(non_dropout + dropout)
        pattern.append(non_dropout)
        pattern.append(dropout)
        pattern.append(non_dropout / (non_dropout + dropout))
        patterns.append(Pattern._make(pattern))
    # Sort pattern with its rate
    patterns.sort(key=lambda p: p[6], reverse=True)
    print('Complete')


# Write patterns.txt
def write_patterns():
    print('Writing pattern file...', end='')
    with open(patternFileName, 'w') as file:
        file.write('{0:>15s}{1:>10s}{2:>10s}{3:>10s}{4:>15s}{5:>10s}{6:>20s}\n'.format(*Pattern._fields))
        for p in patterns:
            file.write('{0:>15s}{1:>10s}{2:>10d}{3:>10d}{4:>15d}{5:>10d}{6:>20.3f}\n'.format(*(tuple(p))))
    print('Complete')


# Distribute patterns to categories
def set_cate():
    print('Distribute patterns...', end='')
    categories.clear()
    for name in cateDict.keys():
        categories.update({name: []})
    for pattern in patterns:
        for name, thd in cateDict.items():
            if pattern.rate >= thd[0]:
                categories[name].append(pattern.num)
                break
    print('Complete')


# Write category file
def write_cate():
    print('Writing category file...', end='')
    with open(categoryFileName, 'w') as file:
        for name, ptns in categories.items():
            file.write(name + '\n')
            for pattern in ptns:
                file.write(num2sym(pattern) + '\t' + pattern + '\n')
            file.write(divider + '\n')
    print('Complete')


# Weight getter
def get_weight(clickstream):
    weight = []
    norm = distance.norm(clickstream)
    for ptns in categories.values():
        weight_sum = 0
        for pattern in ptns:
            weight_sum += distance.cosw(pattern, clickstream, norm)
            weight_sum += distance.lvw(pattern, clickstream, w1=0, w2=1, w3=1)
            weight_sum += distance.lvw(pattern, clickstream, w1=0.1, w2=1, w3=1)
        weight.append(weight_sum)
    return weight


# Compute all clickstreams' weight avg
def get_weight_avg():
    print('Computing weight...', end='')
    weights.clear()
    avg = [0]*len(categories)
    for clickstream_num in clickstreams_num[0:testNum]:
        weight = get_weight(clickstream_num.num)
        avg = [a + b for a, b in zip(avg, weight)]
        weights.append(OrderedDict(zip(list(cateDict.keys())+['non_dropout'], weight+[clickstream_num.non_dropout])))
        # weights.append(Weight._make(weight + [clickstream_num.non_dropout]))
    avg = [w / testNum for w in avg]
    print('Complete')
    return avg


# IPI getter
def get_ipi(weight):
    ipi = 0
    for name, thd in cateDict.items():
        ipi += thd[1]*-1 if weight[name] < weight_avg[name] else thd[1]
    return ipi


# Write IPI file
def write_ipi():
    print('Compute IPI...', end='')
    with open(ipiFileName, 'w') as file:
        file.write('{0:>15s}{1:>60s}{2:>20s}{3:>20s}{4:>20s}{5:>20s}{6:>15s}{7:>10s}\n'.format(\
            *(('username', 'moule_id') + tuple(weight_avg.keys())) + ('IPI',)))
        ipis = []
        cur = views[0].username
        for view, weight in zip(views[0:testNum], weights):
            cur_ipi = get_ipi(weight)
            ipis.append(cur_ipi)
            if view.username != cur:
                cur = view.username
                file.write('{0:>15s}{1:>165f}\n'.format('~~'+cur, sum(ipis)/len(ipis)))
                ipis.clear()
            file.write('{0:>15s}{1:>60s}{2:>20f}{3:>20f}{4:>20f}{5:>20f}{6:>15s}{7:>10d}\n'.format(\
                *((view.username, view.module_id) + tuple(weight.values())) ,cur_ipi))
        file.write('{0:>15s}{1:>165f}\n'.format('~~' + cur, sum(ipis) / len(ipis)))
    print('Complete')

''' Start analysis '''
# Level 2
read_event()
# testNum = len(clickstreams_num)
analyze_patterns()
write_patterns()
set_cate()
write_cate()
weight_avg = OrderedDict(zip(list(cateDict.keys()) + ['non_dropout'], get_weight_avg() + [1]))
write_ipi()
