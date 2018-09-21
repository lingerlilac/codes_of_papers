import re
import numpy as np
import matplotlib.pyplot as plt
import gc
import MySQLdb
con = MySQLdb.Connection(host="localhost", user="root",
                         passwd="lin", port=3306)
cur = con.cursor()
con.select_db('recordworking')
try:
    fil = open("getdata.txt", "r")
except:
    print "file open failed"
    exit()
try:
    iwget = open("iwget.txt", "w")
except:
    print "file open failed"
    exit()
try:
    queueget = open("queueget.txt", "w")
except:
    print "file open failed"
    exit()
try:
    beaconget = open("beaconget.txt", "w")
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
    time = np.uint64(time)
    # print time
    time_list.append(time)
time_list.sort()
for i in time_list:
    sql = "select * from iw where time < (%lu + 10) and time > (%lu - 10);" % (
        i, i)
    cur.execute(sql)
    results = cur.fetchall()
    for r in results:
        iwget.write(str(r) + '\n')
    sql1 = "select * from queue where time < (%lu + 10) and \
    time > (%lu - 10);" % (i, i)
    cur.execute(sql1)
    results1 = cur.fetchall()
    for k in results1:
        queueget.write(str(k) + '\n')
    sql2 = "select * from Beacon where time < (%lu + 100) and \
    time > (%lu - 100);" % (i, i)
    cur.execute(sql2)
    results2 = cur.fetchall()
    for m in results2:
        beaconget.write(str(m) + '\n')
    # tmp = str(i) + '\n'
    # timewrite.write(tmp)
# for i in range(1, len(time_list)):
#     tmp = time_list[i] - time_list[0]
#     tmp = tmp - (tmp % 1000)
#     try:
#         time_record[tmp] += 1
#     except:
#         time_record[tmp] = 1


# time_record1 = sorted(time_record.iteritems(), key=lambda d: d[0])
# for i in time_record1:
#     time_draw.append(i[0])
#     dup.append(i[1])

# plt.figure(1)

# plt.xlabel('Time')
# plt.ylabel('Dupacks')

# plt.plot(time_draw, dup, 'ro', label='dup')

# plt.legend(loc='upper left')
# plt.show()


del dup, time_draw, time_list, time_record
if fil:
    fil.close()
if iwget:
    iwget.close()
if cur:
    cur.close()
if con:
    con.close()
if queueget:
    queueget.close()
if beaconget:
    beaconget.close()
gc.collect()
