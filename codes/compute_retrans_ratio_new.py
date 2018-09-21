#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
from decimal import *
import os
try:
    fil_winsize = codecs.open("list.txt", "r", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    winsize = csv.reader(fil_winsize)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "winsize_filelist open failed"
    exit()
ratio = 1000
for i in winsize:
    i = i[0]
    i = i + '/split/'
    res = os.listdir(i)
    print res
    flist = []
    for j in res:
        if j.find('_winsize') > 0:
            j = i + j
            flist.append(j)
    for k in flist:
        print k
        wfile = 'new/' + k.replace('/', '_')
        rfile = wfile
        wfile = wfile.replace('winsize', 'ratio')
        print wfile, rfile
        # continue
        try:
            f_tmp = open(k, 'rb')
            r_tmp = open(rfile, 'rb')
            results = f_tmp.readlines()
            wfhandle = open(wfile, 'wb')
            write_record = csv.writer(wfhandle)
        except Exception:
            print f_tmp, wfile, 'open falied'
        if f_tmp:
            f_tmp.close()
        re_results = r_tmp.readlines()
        begin_time = re_results[0]
        begin_time = int(begin_time)
        end_time = re_results[len(re_results) - 2]
        end_time = int(end_time)
        duration = int(end_time / ratio) - int(begin_time / ratio)
        # print begin_time, end_time, duration

        # duration = int(duration)
        wintimes = [0.0 for a in range(duration + 1000)]

        for item in results:
            try:
                (mac_addr, eth_src, eth_dst, ip_src,
                    ip_dst, srcport, dstport, sequence, ack_sequence,
                 windowsize, cal_windowsize, timex,
                 datalength, flags, kind, length, wscale) = re.split(",", item)
            except Exception:
                # print item, "sss"
                break
            try:
                timex = int(timex)
            except Exception:
                continue
            timex = timex - begin_time
            timex = timex / ratio
            try:
                wintimes[timex] += 1.0
            except Exception:
                continue
        del results
        gc.collect()

        res_dic = {}
        for i in re_results:
            i = int(i)
            i = i - begin_time
            i = i / ratio
            try:
                res_dic[i] += 1.0
            except Exception:
                res_dic[i] = 1.0
        # print res_dic
        for i in range(0, duration):
            tmp = 0
            try:
                tmp = res_dic[i]
                # print tmp, wintimes[i]
                wintimes[i] = round(tmp / wintimes[i], 4)
            except Exception:
                wintimes[i] = 0.0
        # print wintimes
        tmp1 = int(begin_time / ratio)
        for i in range(0, duration + 1):
            tmp = (tmp1 + i)
            write_record.writerow([tmp, wintimes[i]])

        if wfhandle:
            wfhandle.close()
        # exit()

del winsize
if fil_winsize:
    fil_winsize.close()
gc.collect()
