import re
import numpy as np
import matplotlib.pyplot as plt
import gc
import MySQLdb
con = MySQLdb.Connection(host="localhost", user="root",
                         passwd="lin", port=3306)
cur = con.cursor()
con.select_db('recordworking')
try:
    fil = open("packetsinwisize.txt", "r")
except:
    print "file open failed"
    exit()
try:
    file1 = open("packetsindropped.txt", "r")
except:
    print "file open failed"
    exit()
try:
    file2 = open("suplus.txt", "w")
except:
    print "file open failed"
    exit()
lines = file1.readlines()
lines = list(lines)
kins = fil.readlines()
kins = list(kins)
sequence_list_winsize = []
for kin in kins:
    kin = re.split(',', kin)
    sequence_list_winsize.append(int(kin[0]))
# print sequence_list_winsize
# exit()
# sequence_list_dropped = []
i = 0
for line in lines:
    i += 1
    if i % 10000 == 0:
        print i, len(lines)
    line = re.split(',', line)
    sequence = int(line[0])
    if sequence in sequence_list_winsize:
        sequence_list_winsize.remove(sequence)
    else:
        # sequence_list_dropped.append(sequence)
        file2.write(str(sequence) + '\n')

del sequence_list_winsize
if fil:
    fil.close()

if file1:
    file1.close()
if file2:
    file2.close()
gc.collect()
