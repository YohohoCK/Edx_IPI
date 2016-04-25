# coding=utf-8
# Author : How How & Yo Ho Ho

from collections import OrderedDict
from collections import namedtuple
from ipi_generate import distance_lib

''' Basic setting '''
# Parameter
pSize = 100
testNum = 300
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
cateWeight = []
categories = OrderedDict([])
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
        for view in map(View._make, [line.split() for line in file.readlines()[0:]]):
            views.append(view)
            num = sym2num(view.Clickstream)
            if num not in clickstreams.keys():
                clickstreams.update({num: [1]})
            else:
                clickstreams[num][0] += 1


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
            cateWeight.append(int(weight))
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
    avg_weight.clear()
    # Compute all type of clickstreams' weight
    for clickstream in clickstreams.keys():
        weight = get_weight(clickstream)
        clickstreams[clickstream].append(weight)


# Compute the average of categories' weight
def get_avg():
    print('Computing average weight...')
    avg = [0] * len(categories)
    for para in clickstreams.values():
        avg = [a + b for a, b in zip(avg, para[1])]
    for w in avg:
        avg_weight.append(w / len(clickstreams))


# Compute type of clickstreams' IPI
def get_all_ipi():
    print('Computing IPI...')
    for stream, para in clickstreams.items():
        weight = para[1]
        ipi = 0
        for i in range(len(cateWeight)):
            ipi += cateWeight[i] * 1 if weight[i] > avg_weight[i] else -1
        clickstreams[stream].append(ipi)


# Write IPI file
def write_ipi():
    with open(ipiFileName, 'w') as file:
        file.write('{0:>20s}{1:>60s}{2:>10s}{3:>15s}{4:>10s}{5:>20s}{6:>20s}{7:>20s}{8:>20s}{9:>20s}\n'.format(
            *tuple(('User', 'Module', 'Duration', 'Non_Dropout', 'IPI')), *(tuple(categories.keys())), *tuple(('Clickstream',))
        ))
        ipis = []
        cur = views[0].User
        for view in views:
            para = clickstreams[sym2num(view.Clickstream)]
            cur_ipi = para[2]
            ipis.append(cur_ipi)
            if view.User != cur:
                file.write('{0:>20s}{1:>95f}\n'.format('~~' + cur, sum(ipis) / len(ipis)))
                cur = view.User
                ipis.clear()
            file.write('{0:>20s}{1:>60s}{2:>10s}{3:>15s}{4:>10d}{5:>20f}{6:>20f}{7:>20f}{8:>20f}\t'.format(
                *tuple((view.User, view.Module, view.Duration, view.Non_Dropout, para[2])), *(tuple(para[1]))
            ))
            file.write(view.Clickstream + '\n')
        file.write('{0:>20s}{1:>95f}\n'.format('~~' + cur, sum(ipis) / len(ipis)))


# The whole level 3 program generates the IPI
def level3():
    read_event()
    read_category()
    get_all_weight()
    get_avg()
    get_all_ipi()
    write_ipi()

level3()
