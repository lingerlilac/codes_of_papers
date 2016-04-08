import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
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


count = 20000

I = [[0 for col in range(4)] for row in range(3)]
I[0][1] = 1
I[0][3] = 1
I[1][0] = 1
I[1][2] = 1
I[2][0] = 1
I[2][3] = 1
q = [[0 for col in range(4)] for row in range(2)]
for m in range(0, 2):
    for n in range(0, 4):
        q[m][n] = Queue.Queue(maxsize=count)

channel = [[0 for col in range(4)] for row in range(2)]
channel_lambda = [0.5, 0.5, 0.5, 0.5]
arrival_lambda = [0.3, 0.15, 0.15, 0.3]
w = [[0 for col in range(3)] for row in range(4)]
step = 0.04
loops = int(0.80 / step)

delay_constraint = [350, 200, 250, 320]
dcf = 0.0

trans_count = [[0 for col in range(loops)] for row in range(2)]
schedule = [[0 for col in range(1)] for row in range(2)]
arrival1 = [[0 for col in range(4)] for row in range(2)]


def Clear_queue():
    for m in range(0, 2):
        for n in range(0, 4):
            while q[m][n].empty() is False:
                q[m][n].get()


for h in range(0, loops):
    print(h)
    for i in range(0, count - 1):
        for m in range(0, 4):
            for n in range(0, 4):
                tmp = np.random.binomial(1, channel_lambda[n], 1)
                channel[m][n] = tmp[0]
        tmp = [0.0 for col in range(4)]
        tmp_1 = 0.0
        for m in range(0, 4):
            tmp_1 += k[m] * float(channel[0][m]) * dav[m]
        for m in range(0, 4):
            if tmp_1 != 0:
                tmp[m] = K * k[m] * \
                    float(channel[0][m]) * dav[m] / tmp_1
            else:
                tmp[m] = 0

        w[0][0] = channel[0][1] * q[0][1].qsize() + channel[0][3] * \
            q[0][3].qsize() + tmp[1] + tmp[3]
        w[0][1] = channel[0][0] * q[0][0].qsize() + channel[0][2] * \
            q[0][2].qsize() + tmp[0] + tmp[2]
        w[0][2] = channel[0][0] * q[0][0].qsize() + channel[0][3] * \
            q[0][3].qsize() + tmp[0] + tmp[3]
        hol = [0 for col in range(4)]
        for m in range(0, 4):
            if q[1][m].empty() is True:
                hol[m] = 0
            else:
                hol[m] = i - q[1][m].queue[0]
        w[1][0] = channel[1][1] * hol[1] + channel[1][3] * hol[3]
        w[1][1] = channel[1][0] * hol[0] + channel[1][2] * hol[2]
        w[1][2] = channel[1][0] * hol[0] + channel[1][3] * hol[3]
        w[2][0] = channel[2][1] * q[2][1].qsize() + channel[2][3] * \
            q[2][3].qsize()
        w[2][1] = channel[2][0] * q[2][0].qsize() + channel[2][2] * \
            q[2][2].qsize()
        w[2][2] = channel[2][0] * q[2][0].qsize() + channel[2][3] * \
            q[2][3].qsize()
        tmp = [0, 0, 0, 0]
        for m in range(0, 4):
            if q[3][m] == 0:
                tmp[m] = 0
            else:
                tmp[m] = 1
        w[3][0] = channel[1][1] * tmp[1] + channel[1][3] * tmp[3]
        w[3][1] = channel[1][0] * tmp[0] + channel[1][2] * tmp[2]
        w[3][2] = channel[1][0] * tmp[0] + channel[1][3] * tmp[3]
        ind = [[0 for col in range(1)] for row in range(4)]
        map1 = [[0 for col in range(4)] for row in range(4)]
        for m in range(0, 4):
            tmp = [0, 1, 2]
            t1 = []
            if w[m].count(max(w[m])) == 3:
                t1 = random.sample(tmp, 1)
                ind[m][0] = t1[0]
            elif w[m].count(max(w[m])) == 2:
                tmp.pop(w[m].index(min(w[m])))
                t1 = random.sample(tmp, 1)
                ind[m][0] = t1[0]
            else:
                ind[m][0] = w[m].index(max(w[m]))
        for m in range(0, 4):
            for n in range(0, 4):
                map1[m][n] = I[ind[m][0]][n]
        for m in range(0, 4):
            for n in range(0, 4):
                if map1[m][n] == 1 and q[m][n].empty() is False and channel[m][n] == 1:
                    tmp3 = q[m][n].get()
                    trans_count[m][h] += 1

        tmp = [0, 0, 0, 0]
        tmp2 = [0, 0, 0, 0]
        for m in range(0, 4):
            for n in range(0, q[0][m].qsize()):
                tmp[m] += i - q[0][m].queue[n]
            tmp2[m] = q[0][m].qsize()
            if q[0][m].empty() is True:
                dav[m] = 0
            else:
                dav[m] = tmp[m] / float(tmp2[m])
        for m in range(0, 4):
            for n in range(0, 4):
                tmp = np.random.binomial(1, arrival_lambda[n], 1)
                if tmp[0] == 1:
                    q[m][n].put(i)
    step = 0.01
    arrival_lambda[0] += step
    arrival_lambda[1] += step/2.0
    arrival_lambda[2] += step/2.0
    arrival_lambda[3] += step
    Clear_queue()

print(arrival_lambda)
plt.figure(1)
x = np.linspace(0.3, 0.3 + loops*step, loops)
plt.xlim(x[0], x[loops-1])
plt.xlabel('Input rate from (0.3, 0.15, 0.15, 0.3) to (0.5, 0.25, 0.25, 0.5), K=600')
plt.ylabel('Total throughputs of algorithms')
plt.plot(x, trans_count[0], label='DAMW')
plt.plot(x, trans_count[1], label='HOL-MW')
plt.plot(x, trans_count[2], label='QL-MW')
plt.plot(x, trans_count[3], label='MaxRate')
plt.legend(loc='upper left')
plt.show()

del I, q, channel, channel_lambda, w, k, K, arrival1
del arrival_lambda, schedule, trans_count
gc.collect()
