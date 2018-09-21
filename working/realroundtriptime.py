
import MySQLdb
import gc
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
# try:
#     fil = open("getdata.txt", "w")
# except:
#     print "file open failed"
#     exit()
try:
    recordfile = open("recordtcp2.txt", "w")
except:
    print "open record file failed"
    exit()
con = MySQLdb.Connection(host="localhost", user="root",
                         passwd="lin", port=3306)
cur = con.cursor()
con.select_db('recordworking')
rtt_down_record_rtt = []
rtt_down_record_sequence = []
rtt_down = {}
rtt_up = {}

resultsamount = 0
sql0 = "select id from winsize order by id desc limit 1;"
cur.execute(sql0)
result = cur.fetchall()
resultsamount = result[0][0]
resultsamount /= 10
last = 0
step = 1000000

while (last + step < resultsamount):
    # sql = "select ip_src, sequence, ack_sequence, time, datalength, flags \
    # from winsize where ip_src in (\"219.217.236.9\", \"192.168.1.116\") \
    # and ip_dst in (\"219.217.236.9\", \"192.168.1.116\") \
    # and srcport in (51413, 7964) and dstport in (51413, 7964);"
    sql = "select id, mac_addr, ip_src, \
    ip_dst, srcport, dstport, sequence, ack_sequence, \
    time, datalength, flags from winsize  where \
    id >= %d and id < %d;" % (last, (last + step))
    cur.execute(sql)
    results = cur.fetchall()
    # results = list(results)
    cond = 0
    # print len(results)
    print last, resultsamount
    last += step
    for i in results:
        (xid, mac_addr, ip_src, ip_dst, srcport, dstport, sequence,
            ack_sequence, time, datalength, flags) = i
        # del i
        # srcport = np.uint32(srcport)
        # dstport = np.uint32(dstport)
        # ip_src = re.sub(".", "", ip_src)
        # ip_dst = re.sub(".", "", ip_dst)
        ip_src = ip_src.replace(".", "")
        ip_dst = ip_dst.replace(".", "")
        sequence = np.uint32(sequence)
        ack_sequence = np.uint32(ack_sequence)
        time = np.uint64(time)
        datalength = np.uint32(datalength)
        tmp = -1
        if datalength != 0:
            try:
                rtt_down[mac_addr + ip_src +
                         str(srcport) + str(sequence + datalength)][5] += 1
                tmp = rtt_down[mac_addr + ip_src +
                               str(srcport) + str(sequence + datalength)][5]
            except:
                rtt_down[mac_addr + ip_src + str(srcport) +
                         str(sequence +
                             datalength)] = [time, datalength, 0, 0, 0, 0]
            tmp1 = -1
            try:
                tmp1 = rtt_down[mac_addr + ip_dst +
                                str(dstport) + str(ack_sequence)][4]
            except:
                pass
            if tmp == 1 and tmp1 == 1:
                try:
                    wifirtt = 0
                    wifirtt = time - \
                        rtt_down[mac_addr + ip_src +
                                 str(srcport) + str(sequence + datalength)][0]
                    print xid, sequence, ack_sequence
                    sql_1 = "select id from winsize where \
                    (sequence + datalength) = %d and id < %d and \
                    id > (%d - 10000);" % (sequence, xid, xid)
                    cur.execute(sql_1)
                    back_results = cur.fetchall()
                    xid1 = -1
                    try:
                        xid1 = back_results[0][0]
                        if xid != -1:
                            sql_2 = "select * from winsize where id <= (%d + 0)\
                             and id >= (%d -0);" % (xid, xid1)
                            cur.execute(sql_2)
                            back_results = cur.fetchall()
                            print "----------------------------------------------------------------------------"
                            for j in back_results:
                                print j
                    except:
                        pass
                    if wifirtt < 2000:
                        rtt_down_record_rtt.append(wifirtt)
                    del rtt_down[mac_addr + ip_dst +
                                 dstport + str(ack_sequence)]
                except:
                    pass
            else:
                pass
        else:
            pass
        try:
            rtt_down[mac_addr + ip_dst +
                     str(dstport) + str(ack_sequence)][4] += 1
        except:
            pass
    del results
del rtt_down
tmp = 0.0
length = float(len(rtt_down_record_rtt))
for i in rtt_down_record_rtt:
    tmp += float(i) / length
avage_rtt = tmp
# avage_rtt = sum(float(rtt_down_record_rtt) / float(len(rtt_down_record_rtt)))
avage_rtt = round(avage_rtt, 2)
avage_rtt = "Avg of RTT: " + str(avage_rtt)
ecdf = sm.distributions.ECDF(rtt_down_record_rtt)
x = np.linspace(min(rtt_down_record_rtt), max(rtt_down_record_rtt), 500)
y = ecdf(x)
# matplotlib.rc('xtick', labelsize=20)
# matplotlib.rc('ytick', labelsize=20)
font = {'size': 20}
# print rtt_down_record_rtt
matplotlib.rc('font', **font)
plt.figure(1)
# x = np.linspace(0, count, count)
# plt.xlim(rtt_down_record_sequence[0], rtt_down_record_sequence[
# len(rtt_down_record_sequence) - 1])
# plt.ylim(0, count)
# plt.xlim(0, 1000)
plt.xlim(min(x), max(x))
plt.xlabel('time (ms)')
plt.ylabel('CDF')
# plt.gca().set_xscale('log')
# plt.plot(rtt_down_record_sequence, rtt_down_record_rtt, label=avage_rtt)
plt.plot(x, y, label=avage_rtt)
legend = plt.legend(loc='lower right', fontsize=20)
# legend.get_title().set_fontsize(fontsize=40)
plt.show()

del rtt_down_record_rtt, rtt_down_record_sequence, rtt_up
if cur:
    cur.close()
if con:
    con.close()
gc.collect()
