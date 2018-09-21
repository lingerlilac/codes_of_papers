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
        print wfile
        try:
            f_tmp = open(k, 'rb')
            results = f_tmp.readlines()
            wfhandle = open(wfile, 'wb')
            write_record = csv.writer(wfhandle)
        except Exception:
            print f_tmp, wfile, 'open falied'
        if f_tmp:
            f_tmp.close()
        retrans_dic = {}
        retrans_pkt = []
        min_timex = 0
        for item in results:
            try:
                (mac_addr, eth_src, eth_dst, ip_src,
                    ip_dst, srcport, dstport, sequence, ack_sequence,
                 windowsize, cal_windowsize, timex,
                 datalength, flags, kind, length, wscale) = re.split(",", item)
            except Exception:
                # print item, "sss"
                break
            # key = float(key)
            key = sequence
            try:
                timex = int(timex)
            except Exception:
                continue
            datalength = int(datalength)
            if datalength == 0:
                continue
            try:
                tmp = retrans_dic[key]
                retrans_dic[key].append(timex)
            except Exception:
                retrans_dic[key] = [timex]

        for key in retrans_dic.keys():
            if len(retrans_dic[key]) > 1:
                retrans_pkt += retrans_dic[key][0:(len(retrans_dic[key]) - 1)]
                # print retrans_pkt
        # print retrans_pkt
        retrans_pkt = sorted(retrans_pkt)
        for i in retrans_pkt:
            write_record.writerow([i])
        if wfhandle:
            wfhandle.close()
    # break

if fil_winsize:
    fil_winsize.close()
