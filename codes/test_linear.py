import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sys
fname = sys.argv[1]
# print fname
# exit()
try:
    f_f = open(fname, 'rb')
    r_r = csv.reader(f_f)
except Exception:
    print "debug.csv open falied"

data = []
times = []
base = 0
lines = []
for i in r_r:
    try:
        tm = int(i[0])
    except Exception:
        continue
    pk = int(i[3])
    x = [tm, pk]
    lines.append(x)
lines = sorted(lines)
for i in lines:
    base = int(i[0])
    break

for i in lines:
    tm = int(i[0]) - base
    by = int(i[1])
    data.append(by)
    times.append(tm)
plt.plot(times, data, 'ro')
# plt.axis([0, 6, 0, 20])
plt.show()
