# coding=utf-8
# Author : How How & Yo Ho Ho

from collections import OrderedDict
from collections import namedtuple
from ipi_generate import distance_lib

''' Basic setting '''
# Parameter
pSize = 100
testNum = 500
divider = '--------------------'
eventFileName = 'user_events.txt'
categoryFileName = 'category.txt'
ipiFileName = 'ipi.txt'
# Data type
View = namedtuple('View', ['User', 'Module', 'Duration', 'Start', 'End', 'Clickstream', 'Non_Dropout'])
Category = namedtuple('Category', ['Name', 'Weight', 'Patterns'])
# Pattern in number form
symbol2num = OrderedDict([('Pl', '0'), ('Pa', '1'), ('SSf', '2'), ('SSb', '3'), ('Sf', '4'), ('Sb', '5'), ('St', '6')])
num2symbol = OrderedDict(zip(symbol2num.values(), symbol2num.keys()))
# Category parameter
# data
views = []
clickstreams = {}
cateWeight = OrderedDict([])
categories = OrderedDict([])
weights = []
avg_weight = []

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
    print('Reading event file...')
    views.clear()
    clickstreams.clear()
    with open(eventFileName, 'r') as file:
        for view in map(View._make, [line.split() for line in file.readlines()[0:testNum]]):
            views.append(view)
            num = sym2num(view.Clickstream)
            if num not in clickstreams.keys():
                clickstreams.update({num: []})


# Read category file
def read_category():
    print('Reading category file...')
    cateWeight.clear()
    categories.clear()
    with open(categoryFileName, 'r') as file:
        while True:
            line = file.readline()
            if line == '':
                break
            name, weight = line.split()
            cateWeight.update({name: weight})
            categories.update({name: []})
            line = file.readline().split()[0]
            while line != divider:
                categories[name].append(sym2num(line))
                line = file.readline().split()[0]


# Compute the clickstream's weight
def get_weight(clickstream):
    weight = []
    norm = distance_lib.norm(clickstream)
    for patterns in categories.values():
        weight_sum = 0
        for pattern in patterns:
            weight_sum += distance_lib.cos_wt(pattern, clickstream, norm)
            weight_sum -= distance_lib.lv_dis(pattern, clickstream, w1=0, w2=1, w3=1)
            weight_sum -= distance_lib.lv_dis(pattern, clickstream, w1=0.1, w2=1, w3=1)
        weight.append(weight_sum + 2*len(patterns))
    return weight


# Compute type of clickstreams' weight
def get_all_weight():
    print('Computing weight...')
    index = 1
    weights.clear()
    avg_weight.clear()
    avg = [0] * len(categories)
    # Compute all type of clickstreams' weight
    for clickstream in clickstreams.keys():
        weight = get_weight(clickstream)
        clickstreams[clickstream] = weight
        avg = [a + b for a, b in zip(avg, weight)]
        if index % 10 == 0:
            print(index)
        index += 1
    # Save the average of weight for all type of clickstream
    for w in avg:
        avg_weight.append(w / len(clickstreams))


# The whole level 3 program generates the IPI
def level3():
    read_event()
    read_category()
    get_all_weight()

level3()
print(avg_weight)
