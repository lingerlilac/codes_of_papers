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
qm = [0 for col in range(2)]
Ym = [0 for col in range(2)]
count = 50000
V = 1000
k = [1.0, 1.0]
# alpha = 10000.0
Rm = [0 for col in range(2)]
alp = 0.9

for n in range(0, 2):
    qm[n] = Queue.Queue(maxsize=count)
maxvalue = 0.0
max_last = 0.0
r_keep = [0.0 for col in range(2)]
r = [0.0 for col in range(2)]
channel_lambda = [0.3, 0.6]
arrival_lambda = [0.5, 0.7]
channel = [0 for col in range(2)]
schedule = -1
delay_every_step = [[0 for col in range(count)] for row in range(2)]
tran_count = [0 for col in range(2)]
arrival = [0 for col in range(2)]
max_delay = [0 for col in range(2)]


def Channel():
    for n in range(0, 2):
        tmp = np.random.binomial(1, channel_lambda[n], 1)
        channel[n] = tmp[0]


def Arrival(i):
    for m in range(0, 2):
        if Rm[m] == 1 and qm[m].full() is False:
            qm[m].put(i)
            arrival[m] += 1


# def Clear():
#     for m in range(0, 2):
#         while qm[m].empty() is False:
#             qm[m].get()


for i in range(0, count):
    maxvalue = -100000000.0
    max_last = -100000000.0
    for m in range(0, 2):
        r_keep[m] = 0.0
    r[0] = -1.0
    while r[0] <= 1.0:
        r[1] = -1.0
        while r[1] <= 1.0 and (r[0] + r[1]) <= 2.0:
            if r[0] < 0:
                tmp1 = r[0]
            else:
                tmp1 = math.log(1 + r[0])
            if r[1] < 0:
                tmp2 = r[1]
            else:
                tmp2 = math.log(1 + r[1])
            tmp3 = V * (tmp1 + tmp2)
            tmp4 = Ym[0] * r[0] + Ym[1] * r[1]
            maxvalue = tmp3 - tmp4
            if maxvalue > max_last:
                max_last = maxvalue
                r_keep[0] = r[0]
                r_keep[1] = r[1]
            r[1] += 0.025
        r[0] += 0.025
    Channel()
    if qm[0].empty() is False:
        tmp1 = qm[0].qsize() * channel[0]
        # tmp1 = (i - qm[0].queue[0]) * channel[0]
    else:
        tmp1 = 0
    if qm[1].empty() is False:
        tmp2 = qm[1].qsize() * channel[1]
        # tmp2 = (i - qm[1].queue[0]) * channel[1]
    else:
        tmp2 = 0
    if tmp1 > tmp2:
        schedule = 0
    elif tmp1 == tmp2:
        tmp = [0, 1]
        tmp3 = random.sample(tmp, 1)
        schedule = tmp3[0]
    else:
        schedule = 1
    for m in range(0, 2):
        tmp1 = qm[m].qsize()
        tmp = float(tmp1)
        if tmp < Ym[m]:
            Rm[m] = 1
        else:
            Rm[m] = 0
    if qm[schedule].empty() is False and channel[schedule] == 1:
        tmp = i - qm[schedule].get()
        tran_count[schedule] += 1
        if tmp > max_delay[schedule]:
            max_delay[schedule] = tmp
        # print(qm[0].qsize(), qm[1].qsize())
    for m in range(0, 2):
        if qm[m].empty() is False:
            delay_every_step[m][i] = (i - qm[m].queue[0]) * k[m]
        else:
            delay_every_step[m][i] = 0.0
    for m in range(0, 2):
        tmp = Ym[m] - Rm[m] + r_keep[m]
        if tmp > 0:
            Ym[m] = tmp
        else:
            Ym[m] = 0
    Arrival(i)

print(arrival)
plt.figure(1)
x = np.linspace(0, count, count)
plt.xlabel('Time')
plt.ylabel('HOL delay')

plt.plot(x, delay_every_step[0], label='HOL delay, link 0, CL-MW')
plt.plot(x, delay_every_step[1], label='HOL delay, link 1, CL-MW')
plt.legend(loc='lower right')
plt.show()

del count, V, maxvalue, max_last, r_keep, r
del channel, schedule, channel_lambda
del tran_count, arrival_lambda
gc.collect()
