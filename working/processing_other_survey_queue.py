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


def get_dic(a, b):
    a_2_b = {}
    last_index = 0
    len_b = len(b)
    min_b = b[0]
    for i in range(0, len(a)):
        if a[i] >= min_b:
            break
    a = a[i:]
    # print a
    for m in a:
        # print last_index
        if last_index == (len_b - 1):
            a_2_b[m] = b[len_b - 1]
        for n in range(last_index, len_b):
            if b[n] > m:
                # print b[n]
                a_2_b[m] = b[n - 1]
                last_index = n - 1
                break
            elif b[n] == m:
                a_2_b[m] = b[n]
                last_index = n
                break
            else:
                last_index = n
    return a_2_b


try:
    filenamelist = open("x.txt", 'rw')
except Exception:
    print "x.txt open failed"
filenames = filenamelist.readlines()
if filenamelist:
    filenamelist.close()
for i in filenames:
    i = i.replace('\n', '')
    file_read_time = i
    file_write = i.replace('other.txt', 'debug.csv')
    file_write = file_write.replace('bak_new_data/', 'bak_new_data/new/')
    print file_read_time, file_write
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

    count_iw = 0
    count_drop = 0
    count_beacon = 0
    tmp_last = -1
    queue = {}
    survey = {}

    leng = len(lines)
    for j in range(0, leng):
        item = lines[j]
        # print item
        length = len(item) - 1
        tmp = int(item[0])
        # print item, "before"
        item = item[3:length]
        item = re.split(", ", item)
        item[0] = int(item[0])
        length = len(item)
        # print item
        if tmp == 2:
            # for i in range(4, length):
            #     item[i] = int(item[i])
            count_drop += 1
        elif tmp == 3:
            # for i in range(3, length - 1):
            #     item[i] = int(item[i])
            # try:
            #     item[length - 1] = float(item[length - 1])
            # except Exception:
            #     pass
            count_iw += 1
        elif tmp == 4:
            for i in range(2, length):
                item[i] = int(item[i])
            queue[item[0]] = item + [tmp]
        elif tmp == 5:
            # for i in range(2, 6):
            #     item[i] = int(item[i])
            if tmp_last != 5:
                count_beacon = 0
            count_beacon += 1
        elif tmp == 6:
            for i in range(2, length):
                item[i] = int(item[i])
            item = item + [count_drop, count_iw, count_beacon]
            count_iw = 0
            survey[item[0]] = item + [tmp]
            # print item
        else:
            print "fuck"
        # print item
        tmp_last = tmp
        # if tmp in (4, 6):
        #     item = item + [tmp]
        #     # print item
        #     processed_lines.append(item)
        # print lines[j]

    print tmm.time() - last_time, "2"
    last_time = tmm.time()

    survey_keys = survey.keys()
    survey_keys = sorted(survey_keys, reverse=True)
    len_tmp = len(survey_keys)
    j_found = 1
    print tmm.time() - last_time, "3"
    last_time = tmm.time()
    for j in range(0, len_tmp):
        found = False
        # print survey_keys[j]
        # if j % 10000 == 0:
        #     print j, len_tmp
        m = j_found
        while m < len_tmp:
            if (survey_keys[j] - survey_keys[m]) < 10000:
                m += 1
            else:
                j_found = m
                found = True
                break
        if found is True:
            t1 = survey[survey_keys[j]]
            t2 = survey[survey_keys[j_found]]

            dura = t1[2] - t2[2]
            dura = float(dura)
            if dura == 0:
                continue
            ll = (3, 4, 5, 6, 7, 10)
            for k in ll:
                t1[k] = float(t1[k] - t2[k]) / dura
                t1[k] = round(t1[k], 6)
            survey[survey_keys[j]] = t1
            # print survey[survey_keys[j]]
    print tmm.time() - last_time, "4"
    last_time = tmm.time()
    queue_keys = queue.keys()
    queue_keys = sorted(queue_keys, reverse=True)
    len_tmp = len(queue_keys)
    j_found = 1
    for j in range(0, len_tmp):
        found = False
        # print queue_keys[j]
        m = j_found
        while m < len_tmp:
            if (queue_keys[j] - queue_keys[m]) < 10000:
                m += 1
            else:
                j_found = m
                found = True
                break
        if found is True:
            t1 = queue[queue_keys[j]]
            t2 = queue[queue_keys[j_found]]
            dura = t1[0] - t2[0]
            dura = float(dura)
            if dura == 0:
                continue
            ll = (3, 4, 7, 8)
            for k in ll:
                t1[k] = float(t1[k] - t2[k]) / dura
                t1[k] = round(t1[k], 6)
            queue[queue_keys[j]] = t1
            # print queue[queue_keys[j]]
        # print tmm.time() - last_time, "2"
        # last_time = tmm.time()
        # processed_lines = sorted(processed_lines)
        # print tmm.time() - last_time, "3"
        # last_time = tmm.time()
        # # for i in lines:
        # write_record.writerows(processed_lines)
        # print tmm.time() - last_time, "4"
    print tmm.time() - last_time, "5"
    last_time = tmm.time()
    survey_keys = survey.keys()
    queue_keys = queue.keys()
    survey_keys = sorted(survey_keys)
    queue_keys = sorted(queue_keys)
    survey_2_queue = get_dic(survey_keys, queue_keys)
    survey_keys = survey_2_queue.keys()
    survey_keys = sorted(survey_keys)
    print "6"
    for key in survey_keys:
        qk = survey_2_queue[key]
        ttmp = queue[qk]
        (ttime, mac_addr, queue_id, bytes1, packets, qlen,
         backlog, drops, requeues, overlimits, category) = ttmp
        ttmp = []
        exit()

    tlist = sorted(queue.values() + survey.values())
    write_record.writerows(tlist)
    print tmm.time() - last_time, "6"
    last_time = tmm.time()
    if fil2:
        fil2.close()
    if fil1:
        fil1.close()
    del lines
    gc.collect()
gc.collect()
# 1502998137819124, 04:a1:51:96:ca:83, 0, 3602983303, 2552333, 0, 15969,
# 8801, 7075, 0
