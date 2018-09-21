#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
from decimal import *
import sys

# maclist = ("04:a1:51:96:ca:83",
#            "04:a1:51:a3:57:1a",
#            "44:94:fc:82:d9:8e",
#            "04:a1:51:a8:6e:c5",
#            "04:a1:51:96:64:cb",
#            "04:a1:51:a0:65:c0",
#            "04:a1:51:a7:54:f9",
#            "04:a1:51:8e:f1:cb")

file_write = sys.argv[2]
file_winsize = sys.argv[1]

# try:
#     fil = open("getdata.txt", "w")
# except:
#     print "file open failed"
#     exit()
try:
    fil1 = open(file_winsize, "r")
except Exception:
    print "winsize open failed."
    exit()
try:
    fil2 = codecs.open(file_write, "w", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    write_record = csv.writer(fil2)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "tranningdata open failed"
    exit()

rtt_down_record_rtt = []
rtt_down_record_sequence = []
rtt_down = {}
rtt_up = {}

results = csv.reader(fil1)
for i in results:
    # print re.split(",", i)
    # print i, i[0], i[1]
    try:
        (WINSIZE, time, mac_addr, eth_src, eth_dst,
         ip_src, ip_dst, srcport, dstport,
         sequence, ack_sequence, windowsize,
         cal_windowsize, datalength, flags, kind,
         length, wscale, x) = i
    except Exception:
        continue
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
    # print ip_src
    if ip_src.find("1921681") == -1:
        # print i
        # print "here"
        state_sequence_exit = -1
        ack_sequence_exit = -1
        try:
            rtt_down[ip_src +
                     str(srcport) + str(sequence)][5] += 1
            state_sequence_exit = rtt_down[
                ip_src + str(srcport) + str(sequence)][5]
        except:
            if datalength != 0:
                try:
                    rtt_down[ip_src +
                             str(srcport) + str(sequence + datalength)] = [
                        time, datalength, 0, 0, 0, 0]
                except Exception:
                    print time, datalength, 0, 0, 0, 0
            else:
                pass
        try:
            ack_sequence_exit = rtt_down[
                ip_src + str(srcport) + str(sequence)][4]
            # print "there"
        except:
            pass
        if ack_sequence_exit > 0 and state_sequence_exit == 1:
            # print xid, sequence, ack_sequence
            try:
                wifirtt = 0
                wifirtt = time - \
                    rtt_down[ip_src +
                             str(srcport) + str(sequence)][0]
                if wifirtt < 4000:
                    rtt_down_record_rtt.append(wifirtt)
                del rtt_down[ip_src +
                             str(srcport) + str(sequence)]
            except:
                pass
    else:
        # print i
        try:
            rtt_down[ip_dst + str(dstport) + str(ack_sequence)][4] += 1
            # print "here333"
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
if fil1:
    fil1.close()
if fil2:
    fil2.close()
gc.collect()
