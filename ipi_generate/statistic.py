# coding=utf-8
# Author : Yo Ho Ho

from collections import OrderedDict
from collections import namedtuple

ipiFileName = 'IPI_full.txt'
IPI = namedtuple('IPI', ['Skipping', 'Rewatch', 'Clear_Concept', 'Checkback_Reference', 'non_dropout', 'ipi'])

ipis = []


# Read IPI file
def read_ipi():
    ipis.clear()
    relation = OrderedDict([('-8', {'non_dropout': 0, 'dropout': 0}),
                            ('-6', {'non_dropout': 0, 'dropout': 0}),
                            ('-4', {'non_dropout': 0, 'dropout': 0}),
                            ('-2', {'non_dropout': 0, 'dropout': 0}),
                            ('0', {'non_dropout': 0, 'dropout': 0}),
                            ('2', {'non_dropout': 0, 'dropout': 0}),
                            ('4', {'non_dropout': 0, 'dropout': 0}),
                            ('6', {'non_dropout': 0, 'dropout': 0}),
                            ('8', {'non_dropout': 0, 'dropout': 0})])
    with open(ipiFileName, 'r') as file:
        file.readline()
        for ipi in map(IPI._make, [line.split() for line in file.readlines()]):
            ipis.append(ipi)
            if ipi.non_dropout == '0':
                relation[ipi.ipi]['dropout'] += 1
            else:
                relation[ipi.ipi]['non_dropout'] += 1
    for name, value in relation.items():
        print(name, ' : ', value)


read_ipi()
