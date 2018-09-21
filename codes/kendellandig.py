import math
import re
import gc
import csv
from scipy import stats
import numpy as np

file_list = open('dbg.txt', 'rb')
file_list_read = file_list.readlines()
if file_list:
    file_list.close()

ratio = 1000


# try:
#     data1_file = open("data1_queue.csv", 'wb')
#     data1_w = csv.writer(data1_file)
# except Exception:
#     print data1_file, "open failed"
# data1_w.writerows(data1)


def info_gain(x, y, k=None):
    num_d = len(y)
    num_ck = {}
    num_fi_ck = {}
    num_nfi_ck = {}
    for xi, yi in zip(x, y):
        num_ck[yi] = num_ck.get(yi, 0) + 1
        for index, xii in enumerate(xi):
            if not num_fi_ck.has_key(index):
                num_fi_ck[index] = {}
                num_nfi_ck[index] = {}
            if not num_fi_ck[index].has_key(yi):
                num_fi_ck[index][yi] = 0
                num_nfi_ck[index][yi] = 0
            if not xii == 0:
                num_fi_ck[index][yi] = num_fi_ck[index].get(yi) + 1
            else:
                num_nfi_ck[index][yi] = num_nfi_ck[index].get(yi) + 1
    num_fi = {}
    for fi, dic in num_fi_ck.items():
        num_fi[fi] = sum(dic.values())
    num_nfi = dict([(fi, num_d - num) for fi, num in num_fi.items()])
    HD = 0
    for ck, num in num_ck.items():
        p = float(num) / num_d
        HD = HD - p * math.log(p, 2)
    IG = {}
    for fi in num_fi_ck.keys():
        POS = 0
        for yi, num in num_fi_ck[fi].items():
            p = (float(num) + 0.0001) / (num_fi[fi] + 0.0001 * len(dic))
            POS = POS - p * math.log(p, 2)

        NEG = 0
        for yi, num in num_nfi_ck[fi].items():
            p = (float(num) + 0.0001) / (num_nfi[fi] + 0.0001 * len(dic))
            NEG = NEG - p * math.log(p, 2)
        p = float(num_fi[fi]) / num_d
        IG[fi] = round(HD - p * POS - (1 - p) * NEG, 4)
    IG = sorted(IG.items(), key=lambda d: d[1], reverse=True)
    if k == None:
        return IG
    else:
        return IG[0:k]


def red(x, IG):
    feature = dict.fromkeys([fi for fi, v in IG])
    newx = []
    for xi in x:
        newrow = []
        for index, xii in enumerate(xi):
            if feature.has_key(index):
                newrow.append(xii)
        newx.append(newrow)
    return newx


for delta in (0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000):
    data1 = []
    for i in file_list_read:
        i = i.replace('\n', '')
        ratio_f = i.replace('debug', 'ratio')
        # print ratio_f
        # print i
        try:
            f_tmp = open(ratio_f, 'rb')
            f_r = csv.reader(f_tmp)
            q_tmp = open(i, 'rb')
            q_r = csv.reader(q_tmp)
        except Exception:
            print f_tmp, 'open failed'
        win_dic = {}
        for j in f_r:
            (time, rat) = j
            time = int(time)
            rat = float(rat)
            win_dic[time] = [rat, 0, 0, 0]
        for j in q_r:
            (time, mac_addr, bytes1,
             packets, qlen, backlog, drops, requeues) = j
            # print time, mac_addr, bytes1, packets, qlen, backlog, drops,
            # requeues
            time = int(time) - delta
            time = time / ratio
            time = int(time)
            qlen = float(qlen)
            backlog = float(backlog)
            try:
                tmp = win_dic[time]
            except Exception:
                continue
            win_dic[time][1] += qlen
            win_dic[time][2] += backlog
            win_dic[time][3] += 1.0
            # exit()
        # tmp_list = []
        for key in win_dic.keys():
            if win_dic[key][3] > 0:
                win_dic[key][1] = round(win_dic[key][1] / win_dic[key][3], 4)
                win_dic[key][2] = round(win_dic[key][2] / win_dic[key][3], 4)
                win_dic[key][3] = round(win_dic[key][3] / win_dic[key][3], 4)
                tmp = win_dic[key]
                data1.append(tmp)
        # break
        if f_tmp:
            f_tmp.close()
        if q_tmp:
            q_tmp.close()
    del i
    gc.collect()
    print len(data1)
    y = []
    data = []
    # lines = fil.readlines()
    # lines = list(lines)
    for k in data1:
        # if len(k) < 10:
        #     continue
        (ratio, Qlen, Backlog, amount) = k
        x = [ratio, Qlen, Backlog]
        for i in range(0, len(x)):
            x[i] = float(x[i])
        data.append(x)
        # retrans = int(retrans)
        y.append(ratio)
    x = ("ratio", "Qlen", "Backlog")

    IG = info_gain(data, y)
    # print IG
    print "iGGGGGGGGGGGGGGGGG"
    for k, v in IG:
        try:
            print x[k], v
        except Exception:
            print k, len(x)
    data = np.matrix(data).T
    print "begin ---------------", delta, "-----------------------"
    # print delta
    for i in range(0, len(x)):
        try:
            print x[i], 'a', stats.kendalltau(data[i, ], data[0, ])
        except Exception:
            print i, 'abc'
    del data1
gc.collect()
