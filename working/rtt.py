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

results = csv.reader(fil1)
uplink = {}
downlink = {}
client_ask = []
sender_ask = []
rtt = []
calculated = {}
for i in results:
    try:
        (WINSIZE, time, mac_addr, eth_src, eth_dst,
         ip_src, ip_dst, srcport, dstport,
         sequence, ack_sequence, windowsize,
         cal_windowsize, datalength, flags, kind,
         length, wscale, x) = i
    except Exception:
        continue
    # print time, eth_src, eth_dst, srcport, dstport, datalength
    sequence = int(sequence)
    ack_sequence = int(ack_sequence)
    time = int(time)
    datalength = int(datalength)

    if eth_src == " 6c:e8:73:57:a5:22":
        # print mac_addr
        # uplink.append([time, eth_src, eth_dst, srcport, dstport, datalength])
        key = ack_sequence
        try:
            uplink[key].append([time, datalength])
        except Exception:
            uplink[key] = []
            uplink[key].append([time, datalength])
    elif eth_dst == " 6c:e8:73:57:a5:22":
        if datalength == 0:
            continue
        tmp = 0
        try:
            tmp = calculated[sequence]
        except Exception:
            pass
        if tmp == 1:
            continue
        try:
            tmp = uplink[sequence]
            time1 = uplink[sequence][0][0]
            # print time1, time, uplink[sequence], sequence
            duration = time - time1
            if duration > 5000000 or duration <= 0:
                continue
            rtt.append(duration / 1000)
            calculated[sequence] = 1
        except Exception:
            pass
# print uplink
del calculated, uplink, downlink
tmp = 0.0
length = float(len(rtt))
for i in rtt:
    tmp += float(i) / length
avage_rtt = tmp
# avage_rtt = sum(float(rtt) / float(len(rtt)))
avage_rtt = round(avage_rtt, 2)
avage_rtt = "Avg of RTT: " + str(avage_rtt)
ecdf = sm.distributions.ECDF(rtt)
x = np.linspace(min(rtt), max(rtt), 500)
y = ecdf(x)
# matplotlib.rc('xtick', labelsize=20)
# matplotlib.rc('ytick', labelsize=20)
font = {'size': 20}
# print rtt
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
# plt.plot(rtt_down_record_sequence, rtt, label=avage_rtt)
plt.plot(x, y, label=avage_rtt)
legend = plt.legend(loc='lower right', fontsize=20)
# legend.get_title().set_fontsize(fontsize=40)
plt.show()

if fil1:
    fil1.close()
if fil2:
    fil2.close()
gc.collect()
