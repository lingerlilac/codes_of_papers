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
q = [[0 for col in range(2)] for row in range(2)]
Z = [[0.0 for col in range(2)] for row in range(2)]
q_neely = [0 for col in range(2)]
count = 20000
loops = 50
V = 0.01
v = [0.33, 0.66]
step = 1000.0 / float(loops)
k = [0.0, 0.0]
w = [0.0 for col in range(2)]
Rw = [[0 for col in range(2)] for row in range(2)]
alp = 0.9
for m in range(0, 2):
    q[0][m] = Queue.Queue(maxsize=2 * count)
    q[1][m] = Queue.Queue(maxsize=count)
    q_neely[m] = Queue.Queue(maxsize=2 * count)
qw = [[0 for col in range(2)] for row in range(2)]
Zw = [0.0 for col in range(2)]
Hw = [0.0 for col in range(2)]
Yw = [[0.0 for col in range(2)] for row in range(2)]
alpha = [0.0, 0.0]
for m in range(0, 2):
    for n in range(0, 2):
        qw[m][n] = Queue.Queue(maxsize=count)
maxvalue = [0.0 for col in range(4)]
max_last = [0.0 for col in range(4)]
r_keep = [[0.0 for col in range(2)] for row in range(2)]
r = [[0.0 for col in range(2)] for row in range(2)]
channel_lambda = [0.5, 0.6]
arrival_lambda = [0.2, 1.0]
channel = [[0 for col in range(2)] for row in range(2)]
schedule = [0 for col in range(2)]
drop_decision = [[0 for col in range(2)] for row in range(2)]
delay_record = [[[0.0 for col in range(loops)]
                 for col in range(2)] for row in range(2)]
delay_every_step = [[0 for col in range(2)] for row in range(2)]
tran_count = [[0 for col in range(2)] for row in range(2)]
drop_count = [[0 for col in range(2)] for row in range(2)]
arrival = [[0 for col in range(2)] for row in range(2)]
max_delay_record = [[[0.0 for col in range(loops)]
                     for col in range(2)] for row in range(2)]
max_delay = [[0 for col in range(2)] for row in range(2)]
trans_record = [[[0.0 for col in range(loops)]
                 for col in range(2)] for row in range(2)]


def Channel():
    for m in range(0, 2):
        for n in range(0, 2):
            tmp = np.random.binomial(1, channel_lambda[n], 1)
            channel[m][n] = tmp[0]


def Arrival(i):
    for m in range(0, 2):
        tmp = 0
        tmp = np.random.binomial(1, arrival_lambda[m], 1)
        if q[0][m].full() is False and tmp[0] == 1 and q[1][m].full() is False and q_neely[m].full() is False:
            q[0][m].put(i)
            q[1][m].put(i)
            arrival[0][m] += 1
            arrival[1][m] += 1
            q_neely[m].put(-1)
            # print(q[0][m].qsize())
            # print(q[1][m].qsize())
        elif q[0][m].full() is True:
            print('queue', m, 'is full')
        elif q[1][m].full() is True:
            print('queue', 1, m, 'is full')
        elif q_neely[m].full() is True:
            print('queue_neely', m, 'is full')
        for n in range(0, 2):
            if Rw[m][n] == 1 and qw[m][n].full() is False:
                qw[m][n].put(i)
                arrival[2 + m][n] += 1
                # print(qw[m][n].qsize())
            elif qw[m][n].full() is True:
                print('queue mw is full')


def Clear():
    for m in range(0, 2):
        for n in range(0, 2):
            while q[m][n].empty() is False:
                q[m][n].get()
            while qw[m][n].empty() is False:
                qw[m][n].get()
            Z[m][n] = 0.0
            Yw[m][n] = 0.0
            Rw[m][n] = 0
        Zw[m] = 0.0
        Hw[m] = 0.0
        while q_neely[m].empty() is False:
            q_neely[m].get()


for j in range(0, loops):
    print(j)
    for i in range(0, count):
        # initialization of maxvalue, R
        # get r_keep
        for m in range(0, 4):
            maxvalue[m] = -100000000.0
            max_last[m] = -100000000.0
            for n in range(0, 2):
                r_keep[m][n] = 0.0

        for m in range(0, 4):
            r[m][0] = -1.0
        while r[0][0] <= 1.0:
            for m in range(0, 4):
                r[m][1] = -1.0
            tmp1 = [[0.0 for col in range(2)] for row in range(4)]
            tmp2 = [0.0, 0.0, 0.0, 0.0]
            tmp3 = [0.0, 0.0, 0.0, 0.0]
            tmp4 = [0.0, 0.0, 0.0, 0.0]
            while r[0][1] <= 1.0 and (r[0][0] + r[0][1]) <= 2.0:
                for m in range(0, 4):
                    for n in range(0, 2):
                        if r[m][n] < 0:
                            tmp1[m][n] = v[n] * r[m][n]
                        else:
                            tmp1[m][n] = math.log(1 + v[n] * r[m][n])
                    tmp2[m] = V * (tmp1[m][0] + tmp1[m][1])
                tmp3[0] = Z[0][0] * r[0][0] + Z[0][1] * r[0][1]
                tmp3[1] = Z[1][0] * r[1][0] + Z[1][1] * r[1][1]
                tmp3[2] = Yw[0][0] * r[2][0] + Yw[0][1] * r[2][1]
                tmp3[3] = Yw[1][0] * r[3][0] + Yw[1][1] * r[3][1]
                # 00 hol-neely, 01 hol-neely retranssmission, 10 cl-damw
                # 11 cl-mw
                for m in range(0, 4):
                    maxvalue[m] = tmp2[m] - tmp3[m]
                    if max_last[m] < maxvalue[m]:
                        max_last[m] = maxvalue[m]
                        r_keep[m][0] = r[m][0]
                        r_keep[m][1] = r[m][1]
                for m in range(0, 4):
                    r[m][1] += 0.05
            for m in range(0, 4):
                r[m][0] += 0.05
        # channel process
        Channel()
        # get schedule
        # first hol
        tmp = [[0 for col in range(2)] for row in range(2)]
        for m in range(0, 2):
            for n in range(0, 2):
                if q[m][n].empty() is False:
                    tmp[m][n] = min(i - q[m][n].queue[0],
                                    Z[m][n]) * channel[m][n]
                else:
                    tmp[m][n] = 0
            if tmp[m][0] > tmp[m][1]:
                schedule[m] = 0
            elif tmp[m][0] == tmp[m][1]:
                tmp1 = [0, 1]
                tmp3 = random.sample(tmp1, 1)
                schedule[m] = tmp3[0]
            else:
                schedule[m] = 1
        # then cl-damw and cl-mw
        tmp = [[0 for col in range(2)] for row in range(2)]
        for n in range(0, 2):
            tmp[0][n] = qw[0][n].qsize() * channel[2][n] + (Zw[n] - Hw[n]) * \
                (channel[2][n] * k[n] * w[n] - alpha[n])
        for n in range(0, 2):
            tmp[1][n] = qw[1][n].qsize() * channel[3][n]
        for m in range(0, 2):
            if tmp[m][0] > tmp[m][1]:
                schedule[m + 2] = 0
            elif tmp[m][0] == tmp[m][1]:
                tmp1 = [0, 1]
                tmp3 = random.sample(tmp1, 1)
                schedule[m + 2] = tmp3[0]
            else:
                schedule[m + 2] = 1
        # packet drop
        for m in range(0, 2):
            for n in range(0, 2):
                if q[m][n].empty() is False:
                    tmp = float(i - q[m][n].queue[0])
                else:
                    tmp = 0.0
                drop_decision[m][n] = 0
                if Z[m][n] <= tmp and tmp > 0:
                    drop_decision[m][n] = 1
        for m in range(0, 2):
            for n in range(0, 2):
                if drop_decision[m][n] == 1 and q[m][n].empty() is False:
                    tmp = q[m][n].get()
                    drop_count[m][n] += 1
                    if m == 0:
                        if q_neely[n].empty() is False and q_neely[n].full() is False and q[m][n].full() is False:
                            q_neely[n].get()
                            q[m][n].put(i)
                            q_neely[n].put(tmp)
                        elif q_neely[n].empty() is True:
                            print('queue_neely', n, 'is empty')
                        elif q_neely[n].full() is True:
                            print('queue_neely', n, 'full')
                        else:
                            print('queue', m, n, 'is full')
        # flow control of mw
        for m in range(0, 2):
            for n in range(0, 2):
                tmp1 = qw[m][n].qsize()
                tmp = float(tmp1)
                if tmp <= Yw[m][n]:
                    Rw[m][n] = 1
                else:
                    Rw[m][n] = 0
        # data transmission

        for m in range(0, 2):
            if q[m][schedule[m]].empty() is False and channel[m][schedule[m]] == 1:
                tmp = 0
                if m == 0:
                    if q_neely[schedule[m]].empty() is False:
                        if q_neely[schedule[m]].queue[0] != -1:
                            tmp = i - q_neely[schedule[m]].get()
                            q[m][schedule[m]].get()
                        else:
                            temp = i - q[m][schedule[m]].get()
                            q_neely[schedule[m]].get()
                    else:
                        print('impossible')
                        exit()
                else:
                    tmp = i - q[m][schedule[m]].get()
                delay_every_step[m][schedule[m]] += tmp
                tran_count[m][schedule[m]] += 1
                if tmp > max_delay[m][schedule[m]]:
                    max_delay[m][schedule[m]] = tmp
        for m in range(0, 2):
            if qw[m][schedule[m + 2]].empty() is False and channel[m + 2][schedule[m + 2]] == 1:
                tmp = i - qw[m][schedule[m + 2]].get()
                delay_every_step[m + 2][schedule[m + 2]] += tmp
                tran_count[m + 2][schedule[m + 2]] += 1
                if tmp > max_delay[m + 2][schedule[m + 2]]:
                    max_delay[m + 2][schedule[m + 2]] = tmp

        # updat virtual queues
        # first hol queue
        for m in range(0, 2):
            for n in range(0, 2):
                tmp = Z[m][n] - arrival_lambda[n] + \
                    float(drop_decision[m][n]) + r_keep[m][n]
                if tmp > 0:
                    Z[m][n] = tmp
                else:
                    Z[m][n] = 0
        # Zw, Hw for cl-damw
        for m in range(0, 2):
            tmp = Zw[m] - k[m] * channel[2][m] * w[m] + alpha[m]
            tmp1 = Hw[m] + k[m] * channel[2][m] * w[m] - alpha[m]
            if tmp > 0:
                Zw[m] = tmp
            else:
                Zw[m] = 0
            if tmp1 > 0:
                Hw[m] = tmp
            else:
                Hw[m] = 0
        # Yw for both cl-damw and cl-mw
        tmp = [[0 for col in range(2)] for row in range(2)]
        for m in range(0, 2):
            for n in range(0, 2):
                tmp[m][n] = Yw[m][n] - Rw[m][n] + r_keep[m + 2][n]
                if tmp[m][n] > 0:
                    Yw[m][n] = tmp[m][n]
                else:
                    Yw[m][n] = 0
        Arrival(i)
        
        # for m in range(0, 2):
        #     for n in range(0, 2):
        #         print(q[m][n].qsize(), 1, m, n)
        #         print(qw[m][n].qsize(), 2, m, n)
    print(arrival, tran_count, drop_count)
    for m in range(0, 4):
        for n in range(0, 2):
            if tran_count[m][n] != 0:
                delay_record[m][n][j] = 1.2 * float(
                    delay_every_step[m][n]) / float(tran_count[m][n])
                max_delay_record[m][n][j] = 1.2 *  max_delay[m][n]
            else:
                delay_record[m][n][j] = 0.0
            trans_record[m][n][j] = float(tran_count[m][n]) / float(count)

    for m in range(0, 4):
        for n in range(0, 2):
            delay_every_step[m][n] = 0
            tran_count[m][n] = 0
            max_delay[m][n] = 0
            arrival[m][n] = 0
    for m in range(0, 2):
        for n in range(0, 2):
            drop_count[m][n] = 0
    print(q[0][0].qsize(), q[0][1].qsize(), q_neely[0].qsize(),
          q_neely[1].qsize(), q[1][0].qsize(), q[1][1].qsize())
    print(qw[0][0].qsize(), qw[0][1].qsize(),
          qw[1][0].qsize(), qw[1][1].qsize())
    print(Z, V)
    Clear()
    V = V + step
with open("a.csv", 'a') as outcsv:
    writer = csv.writer(outcsv)
    writer.writerow(delay_record)
    writer.writerow(max_delay_record)
    writer.writerow(tran_count)
plt.figure(1)
x = np.linspace(0, V - 0.01, loops)
plt.xlabel('V')
plt.ylabel('Max Delay and Average Delay')
plt.plot(x, x + 2)
#plt.plot(x, delay_record[0][0], '*-', label='Avg delay, HOL-Neely_no_drop')
# plt.plot(x, delay_record[0][1], '*-', label='Avg, 1, HOL-Neely')
#plt.plot(x, max_delay_record[0][0], '*-', label='Max delay, HOL-Neely_no_drop')
# plt.plot(x, max_delay_record[0][1], '*-', label='Max, 1, HOL-Neely')
plt.plot(x, delay_record[1][0], 's-', label='Avg delay, link 0, CL-DAMW')
plt.plot(x, delay_record[1][1], 'p-', label='Avg delay, link 1, CL-DAMW')
plt.plot(x, max_delay_record[1][0], '*-', label='Max delay, link 0, CL-DAMW')
plt.plot(x, max_delay_record[1][1], 'o-', label='Max delay, link 1, CL-DAMW')
#plt.plot(x, delay_record[2][0], 'p-', label='Avg delay, CL-DAMW')
# plt.plot(x, delay_record[1][1], 'p-', label='Avg, 1, CL-DAMW')
#plt.plot(x, max_delay_record[2][0], 'p-', label='Max delay, CL-DAMW')
# plt.plot(x, max_delay_record[1][1], 'p-', label='Max, 1, CL-DAMW')
#plt.plot(x, delay_record[3][0], 's-', label='Avg delay, MW')
#plt.plot(x, max_delay_record[3][0], 's-', label='Max delay, MW')
# plt.plot(x, max_delay_record[2][1], 's-', label='Max, 1, MW')
plt.legend(loc='upper left')
plt.figure(2)
plt.xlabel('V')
plt.ylabel('Average Throughput')
yline = [0.0 for col in range(loops)]
for m in range(0, loops):
    yline[m] = 0.4
plt.plot(x, yline, label='average throughput')
# plt.plot(x, trans_record[0][0], '*-', label='link 0, HOL-Neely_no_drop')
# plt.plot(x, trans_record[0][1], '*-', label='link 1, HOL-Neely_no_drop')
plt.plot(x, trans_record[1][0], 's-', label='link 0, CL-DAMW')
plt.plot(x, trans_record[1][1], 'p-', label='link 1, CL-DAMW')
# plt.plot(x, trans_record[2][0], 'p-', label='link 0, CL-DAMW')
# plt.plot(x, trans_record[2][1], 'p-', label='link 1, CL-DAMW')
# plt.plot(x, trans_record[3][0], 's-', label='link 0, QL-MW')
# plt.plot(x, trans_record[3][1], 's-', label='link 1, QL-MW')
plt.legend(loc='lower right')
plt.show()

del q, Z, count, V, loops, maxvalue, max_last, r_keep, r
del channel, schedule, channel_lambda, drop_decision
del tran_count, drop_count, arrival_lambda, trans_record
del qw, Zw, Hw
gc.collect()
