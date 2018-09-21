#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
import matplotlib
import matplotlib.pyplot as plt
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

file_write = sys.argv[3]
file_winsize = sys.argv[1]
file_other = sys.argv[2]
# print sys.argv[1], sys.argv[2]
# exit()
try:
    fil2 = codecs.open(file_write, "w", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    write_record = csv.writer(fil2)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "tranningdata open failed"
    exit()

try:
    fil1 = open(file_winsize, "r")
except Exception:
    print "winsize open failed."
    exit()

try:
    fil3 = open(file_other, "r")
except Exception:
    print "other open failed."
    exit()

retrans_dic = {}
retrans_pkt = []
min_timex = 0
min_key = ""
time_winsize = fil1.readline()
time_other = fil3.readline()
time_winsize = re.split(",", time_winsize)
time_other = re.split(",", time_other)
time_winsize = time_winsize[1]
time_other = time_other[1]
time_winsize = int(time_winsize)
time_other = int(time_other)

# print time_winsize, time_other, max(time_winsize, time_other)
time_need = max(time_winsize, time_other)

min_timex = time_need

with open(file_winsize, 'rb') as f:
    for item in f:
        try:
            (WINSIZE, timex, mac_addr, eth_src, eth_dst,
             ip_src, ip_dst, sourceaddr, destination,
             sequence, ack_sequence, windowsize,
             cal_windowsize, datalength, flags, kind,
             length, wscale, x) = re.split(",", item)
        except Exception:
            print item
            break
        key = str(int(sequence)) + "." + str(int(ack_sequence))
        # key = float(key)
        timex = int(timex)
        if timex < time_need:
            continue

        if (timex - 24000) > min_timex:
            try:
                if len(retrans_dic[key]) == 1:
                    del retrans_dic[key]
            except Exception:
                pass
        key = Decimal(key)
        key = int(key)
        try:
            tmp = retrans_dic[key]
            retrans_dic[key].append(timex)
        except Exception:
            retrans_dic[key] = [timex]
            if timex < min_timex:
                min_timex = timex
                min_key = key
                print key

for key in retrans_dic.keys():
    if len(retrans_dic[key]) > 1:
        retrans_pkt += retrans_dic[key][0:(len(retrans_dic[key]) - 1)]
# print retrans_pkt
retrans_pkt = sorted(retrans_pkt)
for i in retrans_pkt:
    # print i
    write_record.writerow([i])
del retrans_dic, retrans_pkt
gc.collect()

if fil1:
    fil1.close()

if fil2:
    fil2.close()
