
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

# maclist = ("04:a1:51:96:ca:83",
#            "04:a1:51:a3:57:1a",
#            "44:94:fc:82:d9:8e",
#            "04:a1:51:a8:6e:c5",
#            "04:a1:51:96:64:cb",
#            "04:a1:51:a0:65:c0",
#            "04:a1:51:a7:54:f9",
#            "04:a1:51:8e:f1:cb")

try:
    filenamelist = open("y.txt", 'r')
except Exception:
    print "x.txt open failed"
filenames = filenamelist.readlines()
if filenamelist:
    filenamelist.close()
for i in filenames:
    i = i.replace('\n', '')
    file_read_time = i
    file_write = i.replace("ordered", "computed")
    # print file_read_time, file_write
    # continue
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
    for j in range(leng, -1, -1):
        

gc.collect()
