#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
from decimal import *
import os
import matplotlib.pyplot as plt
try:
    fil_winsize = codecs.open("/home/oneT/data/list.txt", "r", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    winsize = csv.reader(fil_winsize)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "winsize_filelist open failed"
    exit()
ratio = 1000
iw_file_list = []
pre = '/home/oneT/data/'
for i in winsize:
    tmp = i[0] + '/split/'
    # print tmp
    res = os.listdir(pre + tmp)
    # print res
    for j in res:
        if j.find('iw.csv') > 0:
            jj = tmp + j
            iw_file_list.append(jj)
data_list = []
for xx in iw_file_list:
    print xx
    iw_f = pre + xx
    k = xx.replace('/', '_')
    k = k.replace('iw.csv', 'ratio.csv')
    re_f = pre + 'new/' + k
    wr_f = re_f.replace('ratio', 'stats')
    try:
        wr_file = open(wr_f, 'rb')
        wr_r = csv.reader(wr_file)
    except Exception:
        print wr_f, 'open failed'
        continue
    for i in wr_r:
        try:
            (rat, stations, busy, recv, tran, bytes1,
             packets, qlen, backlog, drops, requeues, neibours, drop) = i
        except:
            print i, wr_f
            (rat, stations, busy, recv, tran, bytes1,
             packets, qlen, backlog, drops, requeues, drop) = i
            print i, wr_f
        x = [rat, stations, busy, recv, tran, bytes1, packets,
             qlen, backlog, drops, requeues, neibours, drop]
        for j in range(0, len(x)):
            x[j] = float(x[j])
        data_list.append(x)
        # exit()
    if wr_file:
        wr_file.close()
    # print wr_f
try:
    data_file = open('/home/oneT/data/new/datalist.csv', 'wb')
    write_record = csv.writer(data_file)
except Exception:
    print "file open failed"
write_record.writerows(data_list)
if data_file:
    data_file.close()
del data_list
if fil_winsize:
    fil_winsize.close()
gc.collect()
