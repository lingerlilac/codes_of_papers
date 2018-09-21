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
    fil = open("packetsinwisize.txt", "w")
except:
    print "file open failed"
    exit()
try:
    file1 = open("packetsindropped.txt", "w")
except:
    print "file open failed"
    exit()
sql1 = "select sequence, ack_sequence from winsize limit 1000000;"
cur.execute(sql1)
results = cur.fetchall()
sql2 = "select time from winsize where id = 1000000;"
cur.execute(sql2)
resu = cur.fetchall()
end_time = resu[0][0]
for r in results:
    fil.write(str(r[0]) + ',' + str(r[1]) + '\n')
# file1.write(str(end_time) + '\n')
sql3 = "select sequence, ack_sequence from dropped \
where systime < %d;" % np.uint64(end_time)
cur.execute(sql3)
resul = cur.fetchall()
for r in resul:
    file1.write(str(r[0]) + ',' + str(r[1]) + '\n')

del resu, resul, results

if fil:
    fil.close()
if file1:
    file1.close()
gc.collect()
