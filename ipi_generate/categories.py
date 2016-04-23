# coding=utf-8
# Author : How How & Yo Ho Ho
from collections import OrderedDict
from collections import namedtuple
from ngram import NGram
import operator

""" Basic setting """
nSize = 4
pSize = 100
divider = '--------------------'
eventFileName = 'user_events.txt'
patternFileName = 'pattern.txt'
categoryFileName = 'category.txt'
start_from_pattern = True
# Data type
Clickstream = namedtuple('Clickstream', ['num', 'non_dropout'])
Pattern = namedtuple('Pattern', ['num', 'times', 'count', 'non_dropout', 'dropout', 'rate'])
# Pattern in number form
symbol2num = OrderedDict([('Pl', '0'), ('Pa', '1'), ('SSf', '2'), ('SSb', '3'), ('Sf', '4'), ('Sb', '5'), ('St', '6')])
num2symbol = OrderedDict(zip(symbol2num.values(), symbol2num.keys()))
# Category parameter
cateDict = OrderedDict([('Clear_Concept', [0.40, 3]),
                        ('Rewatch', [0.3, 1]),
                        ('Checkback_Reference', [0.26, -1]),
                        ('Skipping', [0, -3])])
# data
clickstreams = []
patterns = []
categories = OrderedDict([])
weights = []
''' Define functions '''


# change clickstream's symbol to number form
def sym2num(clickstream):
    ans = clickstream
    for key in symbol2num.keys():
        ans = ans.replace(key, symbol2num[key])
    return ans


# change clickstream's symbol to number form
def num2sym(clickstream):
    ans = clickstream
    for key in num2symbol.keys():
        ans = ans.replace(key, num2symbol[key])
    return ans


# Read event file
def read_clickstream():
    print('Reading event file...')
    clickstreams.clear()
    with open(eventFileName, 'r') as file:
        for view in [line.split() for line in file.readlines()]:
            clickstreams.append(Clickstream(sym2num(view[5]), int(view[6])))


# Find top 100 n-gram patterns
def get_top():
    print('Doing N-Gram...')
    top_patterns = {}
    for clickstream in clickstreams:
        n = NGram(N=nSize, pad_len=0, items=[clickstream.num])
        grams = n._grams
        grams2 = dict(zip(grams.keys(), [list(v.values())[0] for v in grams.values()]))
        for k in grams2.keys():
            if k in top_patterns.keys():
                top_patterns[k][2] += grams2[k]
            else:
                top_patterns[k] = [0, 0, grams2[k]]
    top_patterns = sorted(top_patterns.items(), key=operator.itemgetter(1), reverse=True)
    top_patterns = top_patterns[0:pSize if pSize <= len(top_patterns) else len(top_patterns)]
    return dict(zip([ptn[0] for ptn in top_patterns], [ptn[1] for ptn in top_patterns]))


# Analyze patterns' non-dropout rate
def get_rate():
    top_patterns = get_top()
    print('Analyzing patterns...')
    # Counting dropout & non_dropout
    for num, non_dropout in clickstreams:
        if len(num) < nSize:
            continue
        for pattern in top_patterns.keys():
            if pattern in num:
                top_patterns[pattern][non_dropout] += 1
    # Set top 100 patterns' analysis result
    patterns.clear()
    for pattern, para in top_patterns.items():
        count = para[0] + para[1]
        rate = para[1] / count
        patterns.append(Pattern(pattern, para[2], count, para[1], para[0], rate))
    # Sort patterns with their rate
    patterns.sort(key=lambda p: p.rate, reverse=True)


# Write pattern file
def write_patterns():
    print('Writing pattern file...')
    with open(patternFileName, 'w') as file:
        file.write('{0:>15s}{1:>10s}{2:>10s}{3:>15s}{4:>10s}{5:>15s}\n'.format('Pattern', 'Times', 'Count',
                                                                               'Non Dropout', 'Dropout', 'Rate'))
        for p in patterns:
            file.write('{0:>15s}{1:>10d}{2:>10d}{3:>15d}{4:>10d}{5:>15f}\n'.format(num2sym(p.num), p.times, p.count,
                                                                                   p.non_dropout, p.dropout, p.rate))


# Read pattern file
def read_pattern():
    print('Reading pattern file...')
    patterns.clear()
    with open(patternFileName, 'r') as file:
        file.readline()
        for pattern in map(Pattern._make, [line.split() for line in file.readlines()]):
            patterns.append(pattern)


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


'''
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
    norm = distance_lib.norm(clickstream)
    for ptns in categories.values():
        weight_sum = 0
        for pattern in ptns:
            weight_sum += distance_lib.cosw(pattern, clickstream, norm)
            weight_sum += distance_lib.lvw(pattern, clickstream, w1=0, w2=1, w3=1)
            weight_sum += distance_lib.lvw(pattern, clickstream, w1=0.1, w2=1, w3=1)
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
        file.write('{0:>15s}{1:>60s}{2:>20s}{3:>20s}{4:>20s}{5:>20s}{6:>15s}{7:>10s}\n'.format(
            *(('username', 'module_id') + tuple(weight_avg.keys())) + ('IPI',)))
        ipis = []
        cur = views[0].username
        for view, weight in zip(views[0:testNum], weights):
            cur_ipi = get_ipi(weight)
            ipis.append(cur_ipi)
            if view.username != cur:
                cur = view.username
                file.write('{0:>15s}{1:>165f}\n'.format('~~'+cur, sum(ipis)/len(ipis)))
                ipis.clear()
            file.write('{0:>15s}{1:>60s}{2:>20f}{3:>20f}{4:>20f}{5:>20f}{6:>15s}{7:>10d}\n'.format(
                *((view.username, view.module_id) + tuple(weight.values())), cur_ipi))
        file.write('{0:>15s}{1:>165f}\n'.format('~~' + cur, sum(ipis) / len(ipis)))
    print('Complete')

'''
# Start analysis
'''
# Level 2
read_event()
# testNum = len(clickstreams_num)
if justIpi:
    analyze_patterns()
    write_patterns()
    set_cate()
    write_cate()
weight_avg = OrderedDict(zip(list(cateDict.keys()) + ['non_dropout'], get_weight_avg() + [1]))
write_ipi()
'''
if start_from_pattern:
    read_clickstream()
    get_rate()
    write_patterns()
else:
    read_pattern()

