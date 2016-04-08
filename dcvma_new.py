import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import platform
import gc
import math
import random
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

np.random.seed(123)
sysstr = platform.system()
print(sysstr)
if sysstr == 'Windows':
    import queue as Queue
elif sysstr == 'Darwin':
    import Queue
q = [[0 for col in range(2)] for row in range(3)]
Z = [[0.0 for col in range(2)] for row in range(3)]

count = 10000
loops = 10
step = 2000.0 / float(loops)
V = 0.01
v = [0.5, 0.5]
T = 100
theta = [0.0 for col in range(2)]
epsilon = [0.1, 0.1]
d = [200, 400]
D = [0.0, 0.0]

for m in range(0, 2):
    q[0][m] = Queue.Queue(maxsize=count)
    q[1][m] = Queue.Queue(maxsize=count)
    q[2][m] = Queue.Queue(maxsize=count)

step_size = 0.1
maxvalue = [0.0 for col in range(3)]
max_last = [0.0 for col in range(3)]
r_keep = [[0.0 for col in range(2)] for row in range(3)]
r = [[0.0 for col in range(2)] for row in range(3)]
channel_lambda = [0.5, 0.5]
arrival_lambda = [0.3, 0.45]
channel = [[0 for col in range(2)] for row in range(3)]
schedule = [0 for col in range(3)]
drop_decision = [0 for col in range(2)]
delay_record = [[[0.0 for col in range(loops)]
                 for col in range(2)] for row in range(3)]
tran_count = [[0 for col in range(2)] for row in range(3)]
drop_count = [0 for col in range(2)]
arrival = [[[0 for col in range(loops)]
            for col in range(2)] for row in range(3)]
max_delay_record = [[[0.0 for col in range(loops)]
                     for col in range(2)] for row in range(3)]
max_delay = [[0 for col in range(2)] for row in range(3)]
trans_record = [[[0.0 for col in range(loops)]
                 for col in range(2)] for row in range(3)]
drop_record = [[0.0 for col in range(loops)] for rwo in range(2)]
delay_every_step = [[0 for col in range(2)] for row in range(3)]
delay_record_T = [[-1 for col in range(count)] for row in range(2)]
schedule_record = [[0 for col in range(2)] for row in range(3)]
queue_size_record = [
    [[0 for col in range(loops)] for col in range(2)] for row in range(3)]
tran_r = [[[0 for col in range(loops)] for col in range(2)]
          for row in range(3)]


def Channel():
    global channel_lambda, channel
    for m in range(0, 3):
        for n in range(0, 2):
            tmp = np.random.binomial(1, channel_lambda[n], 1)
            channel[m][n] = tmp[0]


def Arrival(i, j):
    global arrival_lambda, q, arrival
    for m in range(0, 3):
        for n in range(0, 2):
            tmp = np.random.binomial(1, arrival_lambda[n], 1)
            if q[m][n].full() is False and tmp[0] == 1:
                q[m][n].put(i)
                arrival[m][n][j] += 1
            elif q[m][n].full() is True:
                print('queue', m, n, 'is full')
                exit()


def Clear():
    global Z
    for m in range(0, 3):
        for n in range(0, 2):
            while q[m][n].empty() is False:
                q[m][n].get()
            Z[m][n] = 0.0

for j in range(0, loops):
    V = 200
    print(j)
    epsilon = [0.01, 0.01]
    theta = [arrival_lambda[0], arrival_lambda[1]]
    # theta = [-1, -1]
    for i in range(0, count):
        for m in range(0, 3):
            maxvalue[m] = -100000000.0
            max_last[m] = -100000000.0
            for n in range(0, 2):
                r_keep[m][n] = 0.0

        for m in range(0, 2):
            r[m][0] = -1.0
        r[2][0] = theta[0]
        while r[0][0] <= 1.0:
            for m in range(0, 2):
                r[m][1] = -1.0
            r[2][1] = theta[1]
            tmp1 = [[0.0 for col in range(2)] for row in range(3)]
            tmp2 = [0.0, 0.0, 0.0]
            tmp3 = [0.0, 0.0, 0.0]
            while r[0][1] <= 1.0 and r[0][1] <= 1.0:
                for m in range(0, 3):
                    for n in range(0, 2):
                        if r[m][n] < 0:
                            tmp1[m][n] = v[n] * r[m][n]
                        else:
                            tmp1[m][n] = math.log(1 + v[n] * r[m][n])
                    tmp2[m] = V * (tmp1[m][0] + tmp1[m][1])
                tmp3[0] = Z[0][0] * r[0][0] + Z[0][1] * r[0][1]
                tmp3[1] = Z[1][0] * r[1][0] + Z[1][1] * r[1][1]
                tmp3[2] = Z[2][0] * r[2][0] + Z[2][1] * r[2][1]
                # 00 hol-neely, 01 hol-neely retranssmission, 10 cl-damw
                # 11 cl-mw
                for m in range(0, 3):
                    maxvalue[m] = tmp2[m] - tmp3[m]
                    if max_last[m] < maxvalue[m]:
                        max_last[m] = maxvalue[m]
                        r_keep[m][0] = r[m][0]
                        r_keep[m][1] = r[m][1]
                for m in range(0, 2):
                    r[m][1] += step_size
                r[2][1] += (1.0 - theta[1]) * step_size / 2.0
            for m in range(0, 2):
                r[m][0] += step_size
            r[2][0] += (1.0 - theta[0]) * step_size / 2.0
        # channel process
        Channel()
        # compute the schedule, first neely
        tmp = [0 for col in range(2)]
        tmp3 = []
        for n in range(0, 2):
            if q[0][n].empty() is False:
                tmp[n] = min(i - q[0][n].queue[0], Z[0][n]) * channel[0][n]
            else:
                tmp[n] = 0
        if tmp[0] > tmp[1]:
            schedule[0] = 0
        elif tmp[0] < tmp[1]:
            schedule[0] = 1
        else:
            tmp1 = [0, 1]
            tmp3 = random.sample(tmp1, 1)
            schedule[0] = tmp3[0]
        # compute the scheule, neely_non-drop
        tmp = [0 for col in range(2)]
        tmp3 = []
        for n in range(0, 2):
            if q[1][n].empty() is False:
                tmp[n] = min(i - q[1][n].queue[0], Z[1][n]) * channel[1][n]
            else:
                tmp[n] = 0
        if tmp[0] > tmp[1]:
            schedule[1] = 0
        elif tmp[0] < tmp[1]:
            schedule[1] = 1
        else:
            tmp1 = [0, 1]
            tmp3 = random.sample(tmp1, 1)
            schedule[1] = tmp3[0]

        # compute the schedule of dcvma
        tmp = [0 for col in range(2)]
        tmp3 = []
        for n in range(0, 2):
            tmp4 = Z[2][n]
            if q[2][n].empty() is True:
                tmp4 = 0
            tmp[n] = tmp4 * channel[2][n] * q[2][n].qsize()
        if tmp[0] > tmp[1]:
            schedule[2] = 0
        elif tmp[0] < tmp[1]:
            schedule[2] = 1
        else:
            tmp1 = [0, 1]
            tmp3 = random.sample(tmp1, 1)
            schedule[2] = tmp3[0]
        for m in range(0, 3):
            for n in range(0, 2):
                if schedule[m] == n:
                    schedule_record[m][n] += 1
        # packet drop process of neely
        for n in range(0, 2):
            if q[0][n].empty() is False:
                tmp = float(i - q[0][n].queue[0])
            else:
                tmp = 0.0
            drop_decision[n] = 0
            if Z[0][n] <= tmp and tmp > 0:
                drop_decision[n] = 1
        for n in range(0, 2):
            if drop_decision[n] == 1 and q[0][n].empty() is False:
                tmp = q[0][n].get()
                drop_count[n] += 1
                # if q[1][n].empty() is False and q[1].[n].full() is False:
                #     q[1][n].get()
                #     q[1][n].put(tmp)
                # elif q[1][n].empty() is True():
                #     print('q', 1, n, 'is empty')
                # else:
                #     print('q', 1, n, 'is full')
        # data transmission
        for m in range(0, 3):
            if q[m][schedule[m]].empty() is False and channel[m][schedule[m]] == 1:
                tmp = i - q[m][schedule[m]].get()
                tran_count[m][schedule[m]] += 1
                delay_every_step[m][schedule[m]] += tmp
                if m == 2:
                    delay_record_T[schedule[m]][i] = tmp
                if tmp > max_delay[m][schedule[m]]:
                    max_delay[m][schedule[m]] = tmp
        #  update the virtual queues
        # firstly, neely
        # Virtual queue Z
        for n in range(0, 2):
            tmp = Z[0][n] - arrival_lambda[n] + \
                float(drop_decision[n]) + r_keep[0][n]
            if tmp > 0:
                Z[0][n] = tmp
            else:
                Z[0][n] = 0
        # H is not needed to be update

        # secondly, neely non-drop
        for n in range(0, 2):
            tmp = Z[1][n] - arrival_lambda[n] + r_keep[1][n]
            if tmp > 0:
                Z[1][n] = tmp
            else:
                Z[1][n] = 0
        # then dva
        for n in range(0, 2):
            if schedule[2] == n:
                mu = float(channel[2][n])
            else:
                mu = 0.0
            tmp = Z[2][n] - mu + r_keep[2][n]
            if tmp > 0:
                Z[2][n] = tmp
            else:
                Z[2][n] = 0

        # Data Arrival
        Arrival(i, j)

        # Collect the delay and throughput informantion
        if i % T == 0:
            delay_of_previous_T = [0, 0]
            for n in range(0, 2):
                coun = [-2 for col in range(T)]
                for m in range(0, T):
                    ind = i - m
                    # print(delay_record_T[n][ind])
                    delay_of_previous_T[n] = delay_of_previous_T[
                        n] + delay_record_T[n][ind]
                    coun[m] = delay_record_T[n][ind]
                tmp1 = T - coun.count(-1)
                if tmp1 == 0:
                    D[n] = 0.0
                else:
                    tmp4 = delay_of_previous_T[n]
                    D[n] = float(tmp4) / float(tmp1)
            for n in range(0, 2):
                if D[n] > d[n] and theta[n] < 1.0:
                    theta[n] += epsilon[n]
                elif D[n] < d[n] and epsilon[n] >= 0.001:
                    epsilon[n] = epsilon[n] / 1.5
                    theta[n] -= epsilon[n]

    for m in range(0, 3):
        for n in range(0, 2):
            if tran_count[m][n] != 0:
                delay_record[m][n][j] = float(
                    delay_every_step[m][n] / tran_count[m][n])
                max_delay_record[m][n][j] = max_delay[m][n]
            else:
                delay_record[m][n][j] = 0.0
                max_delay_record[m][n][j] = 0.0

            trans_record[m][n][j] = float(tran_count[m][n]) / float(count)
            tran_r[m][n][j] = tran_count[m][n]
            queue_size_record[m][n][j] = q[m][n].qsize()
            arrival[m][n][j] = arrival[m][n][j]
    for n in range(0, 2):
        drop_record[n][j] = drop_count[n]
        # update theta, epsilon

    # clear process
    # print(arrival, tran_count)
    # print('schedule count', schedule_record)
    for m in range(0, 3):
        for n in range(0, 2):
            delay_every_step[m][n] = 0
            tran_count[m][n] = 0
            max_delay[m][n] = 0
            schedule_record[m][n] = 0

    for n in range(0, 2):
        drop_count[n] = 0
        for m in range(0, count):
            delay_record_T[n][m] = 0
    Clear()
    print(theta, 'theta')
    # V = V + step
for m in range(0, 3):
    for n in range(0, 2):
        for k in range(0, loops):
            print('arr of', m, n, arrival[m][n][
                  k], 'tran', tran_r[m][n][k], 'qsize', queue_size_record[m][n][k])
            if m == 0:
                print('drop', drop_record[n][k])
plt.figure(1)
x = np.linspace(0, V - 0.01, loops)
plt.xlabel('V')
plt.ylabel('Max Delay and Average Delay')
# plt.plot(x, x + 2)
plt.plot(x, delay_record[0][0], 's-',
         label='Avg delay, link 0, HOL-Neely')
plt.plot(x, delay_record[0][1], 'p-',
         label='Avg delay, link 1, HOL-Neely')
# plt.plot(x, max_delay_record[0][0], '*-',
#          label='Max delay, link 0, HOL-Neely-Ndrop')
# plt.plot(x, max_delay_record[0][1], 'o-',
#          label='Max delay, link 1, HOL-Neely-Ndrop')
plt.plot(x, delay_record[1][0], 's-',
         label='Avg delay, link 0, HOL-Neely-Ndrop')
plt.plot(x, delay_record[1][1], 'p-',
         label='Avg delay, link 1, HOL-neely-Ndrop')
# plt.plot(x, max_delay_record[1][0], '*-', label='Max delay, link 0, HOL-Neely')
# plt.plot(x, max_delay_record[1][1], 'o-', label='Max delay, link 1, HOL-Neely')
plt.plot(x, delay_record[2][0], 's-', label='Avg delay, link 0, DCVMA')
plt.plot(x, delay_record[2][1], 'p-', label='Avg delay, link 1, DCVMA')
# plt.plot(x, max_delay_record[2][0], '*-', label='Max delay, link 0, DCVMA')
# plt.plot(x, max_delay_record[2][1], 'o-', label='Max delay, link 1, DCVMA')
plt.legend(loc='upper right')
plt.figure(2)
plt.xlabel('V')
plt.ylabel('Average Throughput')
yline = [0.0 for col in range(loops)]
for m in range(0, loops):
    yline[m] = 0.375
plt.plot(x, yline, label='average throughput')
plt.plot(x, trans_record[0][0], 's-', label='link 0, HOL-Neely')
plt.plot(x, trans_record[0][1], 'p-', label='link 1, HOL-Neely')
plt.plot(x, trans_record[1][0], 's-', label='link 0, CL-DAMW-Ndrop')
plt.plot(x, trans_record[1][1], 'p-', label='link 1, CL-DAMW-Ndrop')
plt.plot(x, trans_record[2][0], 's-', label='link 0, DCVMA')
plt.plot(x, trans_record[2][1], 'p-', label='link 1, DCVMA')
plt.legend(loc='center right')
plt.show()

del q, Z, count, V, loops, maxvalue, max_last, r_keep, r
del channel, schedule, channel_lambda, drop_decision, delay_record_T
del tran_count, drop_count, arrival_lambda, trans_record
gc.collect()
