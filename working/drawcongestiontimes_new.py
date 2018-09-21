import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
import gc

try:
    fil = open("congestiontimegot.txt", 'r')
except:
    print "openfile failed"
    exit()
lines = fil.readlines()
time_record = []
data_record = []
time_last = np.uint64((lines[0]))

for line in lines:
    time = np.uint64(line)
    # print time
    time = time / 1000
    if time == time_last:
        data_record[len(data_record) - 1] += 1
    else:
        time_record.append(time)
        data_record.append(1)
    time_last = time

# print data_record
exit()
plt.figure(1)

plt.xlim(min(time_record), max(time_record))
plt.xlabel('Time (s)')
plt.ylabel('Cogestion Times')
# plt.gca().set_xscale('log')
# plt.plot(rtt_down_record_sequence, rtt_down_record_rtt, label=avage_rtt)
plt.plot(time_record, data_record, 'ro', label="Cogestion Times")
legend = plt.legend(loc='upper right', fontsize=20)
# legend.get_title().set_fontsize(fontsize=40)
plt.show()

gc.collect()
if fil:
    fil.close()
