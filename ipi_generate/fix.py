# coding=utf-8
# Author : Yo Ho Ho & How How

from collections import namedtuple

eventFileName = 'user_events.txt'
fixFileName = 'user_events_fixed.txt'

View = namedtuple('View', ['User', 'Module', 'Duration', 'Start', 'End', 'Clickstream', 'Non_Dropout'])

views = []


# Read event file
def read_event():
    print('Reading event file...')
    views.clear()
    with open(eventFileName, 'r') as file:
        for view in map(View._make, [line.split() for line in file.readlines()[0:]]):
            views.append(view)


def write_fix():
    with open(fixFileName, 'w') as file:
        for view in views:
            if 'St' in view.Clickstream:
                file.write('{!s}\t{!s}\t{!s}\t{!s}\t{!s}\t{!s}\t{!s}\n'.format(
                    *tuple((view.User, view.Module, view.Duration, view.Start, view.End, view.Clickstream, '1'))
                ))
            else:
                file.write('{!s}\t{!s}\t{!s}\t{!s}\t{!s}\t{!s}\t{!s}\n'.format(*(tuple(view))))


def check_fix():
    views.clear()
    with open(eventFileName, 'r') as file:
        for view in map(View._make, [line.split() for line in file.readlines()[0:]]):
            views.append(view)
    for view in views:
        if 'St' in view.Clickstream and view.Non_Dropout == '0':
            print('not fixed')


read_event()
write_fix()
check_fix()
