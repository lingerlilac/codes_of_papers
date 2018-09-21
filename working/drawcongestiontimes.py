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
    fil = open("getdata.txt", "r")
except:
    print "file open failed"
    exit()
try:
    file1 = open("congestiontimegot.txt", "w")
except:
    print "file open failed"
    exit()
lines = fil.readlines()
for line in lines:
    index1 = line.find('[')
    line = line[index1:]
    line = re.split(',', line)
    (a, b, time, d, e, f, g) = line
    # print time
    file1.write(time + '\n')
if fil:
    fil.close()
if file1:
    file1.close()
gc.collect()
