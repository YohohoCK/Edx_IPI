clickstreams = {'a': [3, [3, 1, 2, 4]], 'b': [2, [5, 7, 4, 2]]}
avg = [0] * 4
for para in clickstreams.values():
    avg = [a + b*para[0] for a, b in zip(avg, para[1])]
print(avg)
