
import MySQLdb
import gc
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
try:
    fil = open("droppedpacketsandtime.txt", "w")
except:
    print "openfile failed"

con = MySQLdb.Connection(host="localhost", user="root",
                         passwd="lin", port=3306)
cur = con.cursor()
con.select_db('recordworking')
time_record = []
data_record = []
time_begin = 0
sql = "select systime from dropped;"
cur.execute(sql)
results = cur.fetchall()
fil.write(str(results[0][0]))
time_last = np.uint64(results[0][0]) / 1000
time_begin = time_last

time_record.append(0)
data_record.append(0)
for i in results:
    time = np.uint64(i[0]) / 1000
    # print time, time_last
    if time == time_last:
        # print "here"
        data_record[len(data_record) - 1] += 1
    else:
        time_record.append(time - time_begin)
        data_record.append(1)
    time_last = time
    # print time - time_begin
    # fil.write(time + '\n')

# print time_record, data_record
# print data_record
for j in range(0, len(time_record)):
    fil.write(str(time_record[j]) + '\t' + str(data_record[j]) + '\n')
plt.figure(1)

plt.xlim(min(time_record), max(time_record))
plt.xlabel('Time (s)')
plt.ylabel('Dropped Times')
# plt.gca().set_xscale('log')
# plt.plot(rtt_down_record_sequence, rtt_down_record_rtt, label=avage_rtt)
plt.plot(time_record, data_record, 'ro', label="Dropped packets")
legend = plt.legend(loc='upper right', fontsize=20)
# legend.get_title().set_fontsize(fontsize=40)
plt.show()

if fil:
    fil.close()
if cur:
    cur.close()
if con:
    con.close()
gc.collect()
