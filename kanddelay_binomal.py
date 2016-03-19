import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import math
import random
import gc
import platform
import csv
np.random.seed(123)
sysstr = platform.system()
print(sysstr)
if sysstr == 'Windows':
    import queue as Queue
elif sysstr == 'Darwin':
    import Queue


count = 20000

I = [[0 for col in range(4)] for row in range(3)]
I[0][1] = 1
I[0][3] = 1
I[1][0] = 1
I[1][2] = 1
I[2][0] = 1
I[2][3] = 1
q = [0 for col in range(4)]
for m in range(0, 4):
    q[m] = Queue.Queue(maxsize=count)
channel = [0 for col in range(4)]
channel_lambda = [0.5, 0.5, 0.5, 0.5]
arrival_lambda = [0.519, 0.2496, 0.2496, 0.519]
w = [0 for col in range(3)]
step = 0.01
loops = int(0.8 / step)

dav = [0.0 for col in range(4)]
delay_constraint = [350, 200, 250, 320]
k = [0.0, 0.0, 0.0, 0.0]
dcf = 0.0
for m in range(0, 4):
    dcf += 1.0 / (delay_constraint[m] * arrival_lambda[m] * channel_lambda[m])
for m in range(0, 4):
    k[m] = 1.0 / (delay_constraint[m] * arrival_lambda[m]
                  * channel_lambda[m] * dcf)
K = 0
for m in range(0, 4):
    arrival_lambda[m] *= 1
trans_count = [0 for col in range(4)]
queue_length = [[0.0 for col in range(loops)] for row in range(4)]
delays = [[0.0 for col in range(loops)] for row in range(4)]
delays_r = [[0 for col in range(count)] for row in range(4)]
delay_count = [0.0, 0.0, 0.0, 0.0]
K_record = [0 for col in range(loops)]


def Clear_queue():
    for m in range(0, 4):
        while q[m].empty() is False:
            q[m].get()


delay_rec = [0.0 for col in range(4)]
through_count = [0 for col in range(4)]
for h in range(0, loops):
    print(h, K)
    K_record[h] = K
    for i in range(0, count - 1):
        for n in range(0, 4):
            tmp = np.random.binomial(1, channel_lambda[n], 1)
            channel[n] = tmp[0]
        tmp = [0.0 for col in range(4)]
        tmp_1 = 0.0
        for m in range(0, 4):
            tmp_1 += k[m] * float(channel[m]) * dav[m]
        for m in range(0, 4):
            if tmp_1 != 0:
                tmp[m] = K * k[m] * float(channel[m]) * dav[m] / tmp_1
            else:
                tmp[m] = 0
        # for m in range(0, 3):
        #     print(tmp[0], tmp[1], tmp[2])
        w[0] = channel[1] * q[1].qsize() + channel[3] * \
            q[3].qsize() + tmp[1] + tmp[3]
        w[1] = channel[0] * q[0].qsize() + channel[2] * \
            q[2].qsize() + tmp[0] + tmp[2]
        w[2] = channel[0] * q[0].qsize() + channel[3] * \
            q[3].qsize() + tmp[0] + tmp[3]

        ind = -1
        map1 = [0 for col in range(4)]
        tmp = [0, 1, 2]
        t1 = [-1]
        if w.count(max(w)) == 3:
            t1 = random.sample(tmp, 1)
            ind = t1[0]
        elif w.count(max(w)) == 2:
            tmp.pop(w.index(min(w)))
            t1 = random.sample(tmp, 1)
            ind = t1[0]
        else:
            ind = w.index(max(w))
        for m in range(0, 4):
            map1[m] = I[ind][m]
        for n in range(0, 4):
            if map1[n] == 1 and q[n].empty() is False and channel[n] == 1:
                tmp2 = q[n].get()
                delays_r[n][i] = float(i - tmp2)
                delay_count[n] += float(i - tmp2)
                trans_count[n] += 1
        tmp = [0, 0, 0, 0]
        tmp2 = [0, 0, 0, 0]
        for m in range(0, 4):
            for n in range(0, q[m].qsize()):
                tmp[m] += i - q[m].queue[n]
            tmp2[m] = q[m].qsize()
            if q[m].empty() is True:
                dav[m] = 0
            else:
                dav[m] = tmp[m] / float(tmp2[m])
        for n in range(0, 4):
            tmp = np.random.binomial(1, arrival_lambda[n], 1)
            if tmp[0] == 1:
                q[n].put(i)
    K += 16
    for n in range(0, 4):
        if trans_count[n] != 0:
            queue_length[n][h] = delay_count[n] / float(trans_count[n])
        else:
            queue_length[n][h] = 0

    Clear_queue()
    for m in range(0, 4):
        trans_count[m] = 0
        dav[m] = 0.0
        delay_count[m] = 0.0
        for n in range(0, count):
            delays_r[m][n] = 0

tmp = [0, 0, 0]
print(arrival_lambda)
print(k)
plt.figure(1)
plt.xlabel('K')
plt.ylabel('Average delay')
plt.plot(K_record, queue_length[0], label='flow 0')
plt.plot(K_record, queue_length[1], label='flow 1')
plt.plot(K_record, queue_length[2], label='flow 2')
plt.plot(K_record, queue_length[3], label='flow 3')

plt.legend(loc='upper center')
plt.show()
del I, q, channel, channel_lambda, w, k, K
del arrival_lambda, queue_length, trans_count
gc.collect()
