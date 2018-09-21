
import MySQLdb
import gc
import re
import numpy as np
try:
    fil = open("getdata.txt", "w")
except:
    print "file open failed"
    exit()
try:
    recordfile = open("recordtcp2.txt", "w")
except:
    print "open record file failed"
    exit()
con = MySQLdb.Connection(host="localhost", user="root",
                         passwd="lin", port=3306)
cur = con.cursor()
con.select_db('recordworking')
count = 0
resultsamount = 0
sql0 = "select id from winsize order by id desc limit 1;"
cur.execute(sql0)
result = cur.fetchall()
resultsamount = result[0][0]
last = 0
step = 1000000
while((last + step) <= resultsamount):
    sql1 = "select distinct id, mac_addr, ip_src, ip_dst, srcport, \
    dstport, sequence, ack_sequence, time, datalength, \
    flags from winsize where id >= %d and id < %d;" % (last, (last + step))
    cur.execute(sql1)
    resu = cur.fetchall()
    seq_record = {}
    wait_del = {}
    current = 0
    for r in resu:
        if current % 10000 == 0:
            print last, resultsamount
        current += 1
        (xid, mac_addr, ip_src, ip_dst, srcport, dstport, sequence,
            ack_sequence, time, datalength, flags) = r
        srcport = int(srcport)
        dstport = int(dstport)
        sequence = int(sequence)
        ack_sequence = int(ack_sequence)
        datalength = int(datalength)
        flags = int(flags)
        if ip_src.find("192.168.1.") != -1:
            ip = ip_src
            port = srcport
            ip1 = ip_dst
            # port1 = dstport
        else:
            ip = ip_dst
            port = dstport
            ip1 = ip_src
            # port1 = srcport
        # if ip != "192.168.1.116":
        #     continue
        port = str(port)
        key = mac_addr + str(ip) + port + str(sequence)
        key1 = mac_addr + str(ip) + port + str(ack_sequence)
        # larger_sequence = sequence + datalength
        # key_larger = str(ip) + port + str(larger_sequence)

        # try:
        #     seq_record[key_larger][5] += 0
        # except:
        #     try:
        #         seq_record[key][5] += 100000
        #     except:
        #         pass
        if datalength != 0:
            try:
                if ack_sequence == seq_record[key][1]:
                    seq_record[key][4] += 1
                else:
                    # seq_record[key].append(ack_sequence)
                    pass
            except:
                seq_record[key] = [sequence, ack_sequence,
                                   time, xid, 1, 0, mac_addr]
        else:
            try:
                wait_del[sequence] = sequence
            except:
                pass
        # if key1 in seq_record.keys():
        try:
            seq_record[key1][5] += 1
        except:
            pass
    # print "here"
    for k in wait_del.keys():
        try:
            del seq_record[k]
        except:
            pass
    for i in seq_record.keys():
        if seq_record[i][5] > 2 and seq_record[i][4] > 1:
            count += seq_record[i][5]
            string = str((i, seq_record[i]))
            fil.write(string)
            fil.write('\n')
            recordfile.write(str(seq_record[i][0]))
            recordfile.write(" ")
            recordfile.write(str(seq_record[i][1]))
            recordfile.write('\n')
    last += step
    del resu, seq_record, wait_del
print count
gc.collect()
if fil:
    fil.close()
if recordfile:
    recordfile.close()
if cur:
    cur.close()
if con:
    con.close()
