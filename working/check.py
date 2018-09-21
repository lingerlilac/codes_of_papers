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
    fil2 = codecs.open(file_write, "w")
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
x = csv.reader(fil1)
y = csv.reader(fil3)
xx = []
yy = []
diff = []
for i in x:
    i = i[0][3:19]
    i = np.uint64(i)
    xx.append(i)

for i in y:
    i = i[0][3:19]
    i = np.uint64(i)
    yy.append(i)
xx = sorted(xx)
yy = sorted(yy)
i_last = 0
j_last = 0
x_len = len(xx)
y_len = len(yy)
for i in range(0, x_len):
    for j in range(j_last, y_len):
        if xx[i] == yy[j]:
            j_last = j
            break
        elif xx[i] < yy[j]:
            # diff.append(xx[i])
            print xx[i]
del x, y
print diff
gc.collect()
if fil1:
    fil1.close()
if fil2:
    fil2.close()

if fil3:
    fil3.close()
