# coding=utf-8
# Author : How How & Yo Ho Ho
from collections import OrderedDict
from collections import namedtuple
from ngram import NGram
import operator

''' Basic setting'''
# Parameter
nSize = 4
pSize = 100
divider = '--------------------'
eventFileName = 'user_events.txt'
patternFileName = 'pattern.txt'
categoryFileName = 'category.txt'
start_from_pattern = False
cateDict = OrderedDict([('Clear_Concept', [0.40, 3]),
                        ('Rewatch', [0.3, 1]),
                        ('Checkback_Reference', [0.26, -1]),
                        ('Skipping', [0, -3])])

# Data type
Clickstream = namedtuple('Clickstream', ['num', 'non_dropout'])
Pattern = namedtuple('Pattern', ['Pattern', 'Times', 'Count', 'Non_Dropout', 'Dropout', 'Rate'])
# Pattern in number form
symbol2num = OrderedDict([('Pl', '0'), ('Pa', '1'), ('SSf', '2'), ('SSb', '3'), ('Sf', '4'), ('Sb', '5'), ('St', '6')])
num2symbol = OrderedDict(zip(symbol2num.values(), symbol2num.keys()))
# data
clickstreams = []
patterns = []
categories = OrderedDict([])
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
        patterns.append(Pattern(num2sym(pattern), para[2], count, para[1], para[0], rate))
    # Sort patterns with their rate
    patterns.sort(key=lambda p: p.Rate, reverse=True)


# Write pattern file
def write_patterns():
    print('Writing pattern file...')
    with open(patternFileName, 'w') as file:
        file.write('{0:>15s}{1:>10s}{2:>10s}{3:>15s}{4:>10s}{5:>15s}\n'.format(*Pattern._fields))
        for p in patterns:
            file.write('{0:>15s}{1:>10d}{2:>10d}{3:>15d}{4:>10d}{5:>15f}\n'.format(*(tuple(p))))


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
    print('Distribute patterns...')
    categories.clear()
    for name in cateDict.keys():
        categories.update({name: []})
    index = 0
    for name, para in cateDict.items():
        for i in range(index, pSize):
            if float(patterns[i].Rate) < para[0]:
                index = i
                break
            categories[name].append(patterns[i].Pattern)


# Write category file
def write_cate():
    print('Writing category file...')
    with open(categoryFileName, 'w') as file:
        for name, ptns in categories.items():
            file.write(name + '\t' + str(cateDict[name][1]) + '\n')
            for pattern in ptns:
                file.write(pattern + '\n')
            file.write(divider + '\n')


# The whole level 2 program generates the category
def level2():
    if start_from_pattern:
        read_clickstream()
        get_rate()
        write_patterns()
    else:
        read_pattern()
    set_cate()
    write_cate()

level2()
