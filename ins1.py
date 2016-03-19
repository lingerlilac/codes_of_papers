import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import math
import random
import gc
import platform

np.random.seed(123)
sysstr = platform.system()
print(sysstr)
if sysstr == 'Windows':
    import queue as Queue
elif sysstr == 'Darwin':
    import Queue

np.random.seed(1242)
dd = 2
B = 4 * dd
count = 20000
loop_count = count * B
alpha = [0.27, 0.25, 0.25, 0.24]
K = 1000000
lis_count = [[0 for col in range(count)] for row in range(4)]
p = [0.25, 0.25, 0.25, 0.25]
# q = [0.5, 0.5, 0.5, 0.5]
flow_count = [0 for col in range(4)]
arr_count = [0 for col in range(4)]
tran_count = [0 for col in range(4)]
lis = [[0 for col in range(count)] for row in range(4)]
Q = [0.0 for col in range(count) for row in range(1)]
D = [0.0 for col in range(count) for row in range(1)]
count_p = [0 for col in range(4)]
count_p2 = [0 for col in range(4)]
for i in range(0, count):
    if (i % 1000) == 0:
        print(i)
    start = [0 for col in range(4)]
    rat = [0 for col in range(4)]
    new_flow = [0 for col in range(4)]
    rate = [0 for col in range(4)]
    for m in range(0, 4):
        start[m] = np.random.binomial(1, alpha[m], 1)
    for m in range(0, 4):
        if start[m][0] == 1:
            new_flow[m] = 1
            lis[m][i] = B
            flow_count[m] += 1
            arr_count[m] += B
    channel = [[0 for col in range(count)] for row in range(4)]
    for m in range(0, 4):
        for k in range(0, i):
            if lis[m][k] != 0:
                rat[m] = np.random.binomial(1, p[m], 1)
                if rat[m][0] == 1:
                    rate[m] = 1
                    count_p[m] += 1
                else:
                    rate[m] = 2
                    count_p2[m] += 1
                channel[m][k] = rate[m]
    l_tmp = [[0 for col in range(count)] for row in range(1)]
    for m in range(0, 1):
        for k in range(0, i):
            l_tmp[m][k] = lis[m][k] * channel[m][k]
    flow = [0 for col in range(4)]
    # print('lis', lis)
    # print('channel', channel)
    for m in range(0, 1):
        flow[m] = l_tmp[m].index(max(l_tmp[m]))
        if lis[m][flow[m]] >= channel[m][flow[m]]:
            lis[m][flow[m]] -= channel[m][flow[m]]
            tran_count[m] += channel[m][flow[m]]
        else:
            tran_count[m] += lis[m][flow[m]]
            lis[m][flow[m]] = 0
        lis_count[m][i] = sum(lis[m])
    for m in range(1, 2):
        flow[m] = channel[m].index(max(channel[m]))
        if lis[m][flow[m]] >= channel[m][flow[m]]:
            lis[m][flow[m]] -= channel[m][flow[m]]
            tran_count[m] += channel[m][flow[m]]
        else:
            tran_count[m] += lis[m][flow[m]]
            lis[m][flow[m]] = 0
        lis_count[m][i] = sum(lis[m])
    delay = [[0 for col in range(count)] for row in range(4)]
    for m in range(2, 4):
        for k in range(0, i):
            if lis[m][k] != 0:
                delay[m][k] = (i - k) * channel[m][k]

    for m in range(2, 3):
        flow[m] = delay[m].index(max(delay[m]))
        if lis[m][flow[m]] >= channel[m][flow[m]]:
            lis[m][flow[m]] -= channel[m][flow[m]]
            tran_count[m] += channel[m][flow[m]]
        else:
            tran_count[m] += lis[m][flow[m]]
            lis[m][flow[m]] = 0
        lis_count[m][i] = sum(lis[m])

    div = [0.0 for col in range(count) for row in range(1)]
    weight_record = [0.0 for col in range(count) for row in range(1)]
    for k in range(0, i):
        if lis[m][k] != 0:
            D[k] = float((i - k)) / float(i) + float(D[k]) / float(i)
            div[k] += channel[3][k] * D[k]
    for k in range(0, i):
        if div[k] == 0:
            tmp = 0
        else:
            tmp = K * (channel[3][k] * D[k]) / div[k]
        weight_record[k] = lis[3][k] * channel[3][k] + tmp
    flow[3] = weight_record.index(max(weight_record))
    if lis[3][flow[3]] >= channel[3][flow[3]]:
        lis[3][flow[3]] -= channel[3][flow[3]]
        tran_count[3] += channel[3][flow[3]]
    else:
        tran_count[3] += lis[3][flow[3]]
        lis[3][flow[3]] = 0
    lis_count[3][i] = sum(lis[3])

for m in range(0, 4):
    print(flow_count[m], count_p[m], count_p2[m], arr_count[m], tran_count[m], lis_count[m][count - 1])
plt.figure(1)
plt.xlim(0, count)
plt.ylim(0, count*0.5)
plt.xlabel("Time")
plt.ylabel("Total queue length")
plt.plot(lis_count[3], label='Stable, DAMW')
plt.plot(lis_count[2], label='Stable, HOL-MW')
plt.plot(lis_count[0], label='Unstable, QL-MW')
plt.plot(lis_count[1], label='Stable, MW-rate')


plt.legend()
plt.show()
del dd, B, count, loop_count, alpha, count_p2, tran_count
del lis, lis_count, p, flow_count, arr_count, count_p
del channel, l_tmp, flow, start, rate, new_flow, rat
del delay, Q, D, weight_record
gc.collect()
