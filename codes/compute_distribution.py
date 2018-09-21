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
    fil_winsize = codecs.open("list.txt", "r", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    winsize = csv.reader(fil_winsize)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "winsize_filelist open failed"
    exit()
ratio = 1000
win_dic = []
stats = []
for i in winsize:
    i = i[0]
    i = i + '/split/'
    res = os.listdir(i)
    print res
    flist = []
    for j in res:
        if j.find('tmp') >= 0:
            continue
        if j.find('queue_processed') >= 0:
            j = i + j
            flist.append(j)
    for k in flist:
        # print k
        wfile = 'new/' + k.replace('/', '_')
        # rfile = wfile.replace('queue')
        wfile = wfile.replace('queue_processed', 'ratio')
        print k, wfile
        # continue
        try:
            f_tmp = open(k, 'rb')
            w_tmp = open(wfile, 'rb')
            queue_items = csv.reader(f_tmp)
            ratio_items = csv.reader(w_tmp)
        except Exception:
            print k, wfile, 'open falied'
            continue

        for j in ratio_items:
            # print i
            try:
                (time, rat) = j
            except Exception:
                print "bbb", j
                continue
            time = int(time)
            rat = float(rat)
            # time = time / ratio
            # time = int(time)
            x = [time, rat]
            win_dic.append(x)
        del ratio_items
        gc.collect()
        for j in queue_items:
            try:
                (mac, time, qid, bytes1, packets,
                 qlen, backlog, drops, requeues) = j
            except Exception:
                print "xxx", j
                continue
            time = int(time)
            qid = int(qid)
            if qid != 3:
                continue
            time = time / ratio
            time = int(time)
            x = [time, bytes1, packets,
                 qlen, backlog, drops, requeues]
            stats.append(x)
        # print que_dic

        if f_tmp:
            f_tmp.close()
        if w_tmp:
            w_tmp.close()
        # print win_dic
        # print que_dic
        # exit()
    # break
ff = open('retrans.csv', 'wb')
write_record = csv.writer(ff)
write_record.writerows(win_dic)
if ff:
    ff.close()
del ff, write_record
gc.collect()
ff = open('stats.csv', 'wb')
write_record = csv.writer(ff)
write_record.writerows(stats)
if ff:
    ff.close()
del stats, win_dic
del winsize
gc.collect()
exit()
x_qlen = np.linspace(0, 1.0, 1000)
print "2"
fig, ((left_axis1, left_axis2)
      ) = plt.subplots(figsize=(12, 9), nrows=1, ncols=2)
# fig.subplots_adjust(right_axis=0,75)
right_axis1 = left_axis1.twinx()

p1, = left_axis1.plot(x_qlen, win_d, 'b.-')
p2, = right_axis1.plot(x_qlen, qlen_d, 'r.-')

left_axis1.set_xlim(0, 1.0)
# left_axis1.set_xticks(np.arange(0,110,10))

left_axis1.set_ylim(0.0, 0.2)
left_axis1.set_yticks(
    np.arange(0.0, 0.2, 0.05))

right_axis1.set_ylim(0.0, 0.00002)
right_axis1.set_yticks(
    np.arange(0.0, 0.00002, 0.000002))

left_axis1.set_xlabel('Qlen (packets)')
left_axis1.set_ylabel('Fraction')
# right_axis1.set_ylabel('Retrans rate')

left_axis1.yaxis.label.set_color(p1.get_color())
right_axis1.yaxis.label.set_color(p2.get_color())

tkw = dict(size=5, width=1.5)
left_axis1.tick_params(axis='y', colors=p1.get_color(), **tkw)
right_axis1.tick_params(axis='y', colors=p2.get_color(), **tkw)
left_axis1.tick_params(axis='x', **tkw)

right_axis2 = left_axis2.twinx()

p1, = left_axis2.plot(x_qlen, win_d, 'b.-')
p2, = right_axis2.plot(x_qlen, qlen_d, 'r.-')

left_axis2.set_ylim(0.0, 0.2)
# left_axis2.set_xticks(np.arange(0,110,10))

left_axis2.set_ylim(0.0, max(win_d))
left_axis2.set_yticks(
    np.arange(0.0, 0.2, 0.05))

right_axis2.set_ylim(0.0, 0.00002)
right_axis2.set_yticks(
    np.arange(0.0, 0.00002, 0.000002))

left_axis2.set_xlabel('Bytes rate (bytes/s)')
left_axis2.set_ylabel('Fraction')
# right_axis2.set_ylabel('Retrans rate')

left_axis2.yaxis.label.set_color(p1.get_color())
right_axis2.yaxis.label.set_color(p2.get_color())

tkw = dict(size=5, width=1.5)
left_axis2.tick_params(axis='y', colors=p1.get_color(), **tkw)
right_axis2.tick_params(axis='y', colors=p2.get_color(), **tkw)
left_axis2.tick_params(axis='x', **tkw)

# right_axis3=left_axis3.twinx()

# p1, = left_axis3.plot(x_packets, value_packets, 'b.-')
# p2, = right_axis3.plot(x_packets, retrans_packets, 'r.-')

# left_axis3.set_xlim(0, 150)
# # left_axis3.set_xticks(np.arange(0,110,10))

# left_axis3.set_ylim(0.0, max(value_packets))
# left_axis3.set_yticks(
#     np.arange(0.0, max(value_packets), max(value_packets) / 2.0))

# right_axis3.set_ylim(0, 2.0 * max(retrans_packets))
# right_axis3.set_yticks(
#     np.arange(0, 2.0 * max(retrans_packets), max(retrans_packets) / 2.0))

# left_axis3.set_xlabel('Packets rate (packets/s)')
# left_axis3.set_ylabel('Fraction')
# # right_axis3.set_ylabel('Retrans rate')

# left_axis3.yaxis.label.set_color(p1.get_color())
# right_axis3.yaxis.label.set_color(p2.get_color())

# tkw=dict(size = 5, width = 1.5)
# left_axis3.tick_params(axis = 'y', colors = p1.get_color(), **tkw)
# right_axis3.tick_params(axis = 'y', colors = p2.get_color(), **tkw)
# left_axis3.tick_params(axis = 'x', **tkw)

# right_axis4=left_axis4.twinx()

# p1, = left_axis4.plot(x_drops, value_drops, 'b.-')
# p2, = right_axis4.plot(x_drops, retrans_drops, 'r.-')

# left_axis4.set_xlim(0, max(x_drops))
# # left_axis4.set_xticks(np.arange(0,110,10))

# left_axis4.set_ylim(0.0, 0.05 * max(value_drops))
# left_axis4.set_yticks(
#     np.arange(0.0, 0.05 * max(value_drops), 0.05 * max(value_drops) / 2.0))

# right_axis4.set_ylim(0, 2.0 * max(retrans_drops))
# right_axis4.set_yticks(
#     np.arange(0, 2.0 * max(retrans_drops), 2.0 * max(retrans_drops) / 2.0))

# left_axis4.set_xlabel('Drop rate (packets/s)')
# left_axis4.set_ylabel('Fraction')
# # right_axis4.set_ylabel('Retrans rate')

# left_axis4.yaxis.label.set_color(p1.get_color())
# right_axis4.yaxis.label.set_color(p2.get_color())

# tkw=dict(size = 5, width = 1.5)
# left_axis4.tick_params(axis = 'y', colors = p1.get_color(), **tkw)
# right_axis4.tick_params(axis = 'y', colors = p2.get_color(), **tkw)
# left_axis4.tick_params(axis = 'x', **tkw)

plt.tight_layout(pad=0.1, h_pad=None, w_pad=None, rect=None)
pic = 'abc' + ".eps"
plt.savefig(pic)
plt.show()

if fil_winsize:
    fil_winsize.close()
gc.collect()
