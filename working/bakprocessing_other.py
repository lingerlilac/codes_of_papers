#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
import matplotlib
import matplotlib.pyplot as plt
from decimal import *
import time as time_linger
import copy
import time as tmm

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
file_read_time = sys.argv[1]


try:
    fil2 = codecs.open(file_write, "w")
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    write_record = csv.writer(fil2)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "tranningdata open failed"
    exit()

try:
    fil1 = open(file_read_time, "r")
except Exception:
    print "6666 or retranstime open failed."
last_time = tmm.time()
lines = fil1.readlines()
print tmm.time() - last_time, "1"
last_time = tmm.time()

leng = len(lines)
for j in range(0, leng):
    item = lines[j]
    # print item
    length = len(item) - 1
    tmp = int(item[0])
    item = item[3:length]
    item = re.split(", ", item)
    item[0] = int(item[0])
    length = len(item)
    if tmp == 2:
        for i in range(4, length):
            item[i] = int(item[i])
    elif tmp == 3:
        for i in range(3, length - 1):
            item[i] = int(item[i])
        try:
            item[length - 1] = float(item[length - 1])
        except Exception:
            pass
    elif tmp == 4:
        for i in range(2, length):
            item[i] = int(item[i])
    elif tmp == 5:
        for i in range(2, 6):
            item[i] = int(item[i])
    elif tmp == 6:
        for i in range(2, length):
            item[i] = int(item[i])
    else:
        print "fuck"
    # print item
    item = [tmp] + item
    # print item
    lines[j] = item
    # print lines[j]
print tmm.time() - last_time, "2"
last_time = tmm.time()
lines = sorted(lines)
print tmm.time() - last_time, "3"
last_time = tmm.time()
# for i in lines:
write_record.writerows(lines)
print tmm.time() - last_time, "4"
if fil2:
    fil2.close()
if fil1:
    fil1.close()
del lines
gc.collect()
