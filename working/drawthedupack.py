import re
import numpy as np
import matplotlib.pyplot as plt
import gc

try:
    fil = open("getdata.txt", "r")
except:
    print "file open failed"
    exit()
lines = fil.readlines()
time_list = []
time_record = {}
time_draw = []
dup = []

for line in lines:
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = re.split(',', line)
    # print line
    try:
        (key, sequence, ack_sequence, time, xid, retrans, dupack, xid) = line
    except:
        print line[0]
        print "line to set failed"
        exit()
    print
    time = np.uint64(time)
    # print time
    time_list.append(time)
time_list.sort()
# print time_list[0], time_list[len(time_list) - 1],
# time_list[len(time_list) - 1] - time_list[0]
for i in range(1, len(time_list)):
    tmp = time_list[i] - time_list[0]
    # print time_list[i] - time_list[0], time_list[i], time_list[0]
    tmp = tmp - (tmp % 1000)
    try:
        time_record[tmp] += 1
    except:
        time_record[tmp] = 1

# print time_list
# print time_record
time_record1 = sorted(time_record.iteritems(), key=lambda d: d[0])
for i in time_record1:
    time_draw.append(i[0])
    dup.append(i[1])

plt.figure(1)
# x = np.linspace(0, count, count)
# plt.ylim(0, count)
plt.xlabel('Time')
plt.ylabel('Dupacks')
# plt.gca().set_yscale('log')
plt.plot(time_draw, dup, 'ro', label='dup')

plt.legend(loc='upper left')
plt.show()


del dup, time_draw, time_list, time_record, time_record1
if fil:
    fil.close()
gc.collect()
