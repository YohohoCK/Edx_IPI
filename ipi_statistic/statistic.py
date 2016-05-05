# coding=utf-8
# Author : Yo Ho Ho & How How

from collections import namedtuple

''' Basic setting'''
style = '_kind_3113'
ipiFileName = 'ipi' + style + '.txt'
countFileName = 'count' + style + '.txt'
userFileName = 'user' + style + '.txt'
clockFileName = 'clock' + style + '.txt'
# Get the field of View in IPI file
View = namedtuple('View', ['User', 'Module', 'Duration', 'Start_Time', 'Non_Dropout', 'IPI',
                           'Clear_Concept', 'Rewatch', 'Checkback_Reference', 'Skipping', 'Clickstream'])
# Data
views = []
''' Statistic functions '''


# Read IPI file
def read_ipi():
    print('Reading IPI file...')
    views.clear()
    with open(ipiFileName) as file:
        file.readline()
        for line in file.readlines():
            para = line.split()
            # Drop = 0, Non_drop = 1
            # Can easily implement in list[0:1] data type, and add ipi at list[2]
            views.append(View(para[0], para[1], int(para[2]), para[3], int(para[4]), int(para[5]),
                              float(para[6]), float(para[7]), float(para[8]), float(para[9]), para[10]))


# Count how many time do dropout & non dropout happen for each ipi value
def count_ipi():
    print('Counting ipi non dropout rate...')
    countDict = {}
    for view in views:
        ipi = view.IPI
        if ipi not in countDict.keys():
            countDict[ipi] = [0, 0]
        countDict[ipi][view.Non_Dropout] += 1
    print('Writing count file...')
    with open(countFileName, 'w') as file:
        file.write('{0:>5s}{1:>15s}{2:>15s}{3:>15s}\n'.format('IPI', 'Dropout', 'Non_Dropout', 'Rate'))
        for ipi, drop in countDict.items():
            file.write('{0:>5d}{1:>15d}{2:>15d}{3:>15f}\n'.format(ipi, drop[0], drop[1], drop[1] / (drop[0]+drop[1])))


# Compute each user's average ipi value
def write_user():
    print('Writing user file...')
    # Collect user's ipi
    userDict = {}
    for view in views:
        name = view.User
        if name not in userDict.keys():
            userDict[name] = [0, 0, 0]
        userDict[name][view.Non_Dropout] += 1
        userDict[name][2] += view.IPI
    # Write user file
    with open(userFileName, 'w') as file:
        file.write('{0:>20s}{1:>10s}{2:>15s}{3:>15s}\n'.format('User', 'Dropout', 'Non_Dropout', 'IPI'))
        for name, para in userDict.items():
            file.write('{0:>20s}{1:>10d}{2:>15d}{3:>15f}\n'.format(name, para[0], para[1], para[2] / (para[0]+para[1])))


# Compare dropout rate and ipi with start time
def write_clock():
    print('Writing clock file...')
    # Compute the performance of each clock
    clocks = [[0, 0, 0] for i in range(24)]
    for view in views:
        time = view.Start_Time
        time = int(time[time.find('T') + 1:].split(':')[0])
        clocks[time][view.Non_Dropout] += 1
        clocks[time][2] += view.IPI
    # Write clock file
    with open(clockFileName, 'w') as file:
        file.write('{0:>10s}{1:>10s}{2:>10s}{3:>15s}{4:>15s}\n'.format('StartTime', 'Dropout', 'Non_Drop', 'Rate', 'IPI'))
        for time in range(24):
            if (clocks[time][0] + clocks[time][1]) != 0:
                clocks[time][2] = float(clocks[time][2]) / (clocks[time][0] + clocks[time][1])
            file.write('{0:>10d}{1:>10d}{2:>10d}{3:>15f}{4:>15f}\n'.format(
                time, clocks[time][0], clocks[time][1], clocks[time][1] / (clocks[time][0]+clocks[time][1]),
                clocks[time][2]
            ))


# Main function
def statistic():
    read_ipi()
    count_ipi()
    write_user()
    write_clock()

statistic()
