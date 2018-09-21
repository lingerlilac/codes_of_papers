#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
import codecs
try:
    fil_winsize = codecs.open("u.txt", "r", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    winsize = csv.reader(fil_winsize)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "winsize_filelist open failed"
    exit()
data = []
for i in winsize:
    i = i[0]
    print i
    try:
        f_tmp = open(i, 'rb')
        results = csv.reader(f_tmp)
    except Exception:
        print ftmp, "open failed"
    for k in results:
        d = k[1]
        d = float(d)
        data.append(d)
        # break
    # print data
    # break
ecdf = sm.distributions.ECDF(data)
avg = sum(data) / float(len(data))
avg = round(avg, 4)
# print avg
avg = 'Avg: ' + str(avg) + '%'
x = np.linspace(min(data), max(data), 10000)
y = ecdf(x)
plt.xlabel('% of retransmission rate')
plt.ylabel('CDF')
plt.xscale('log')
plt.step(x, y, label=avg)
legend = plt.legend(loc='lower right', fontsize=20)
name = "/home/lin/Pictures/cdfofretras"
# print name
pic = name + ".eps"
plt.savefig(pic)
plt.show()

if fil_winsize:
    fil_winsize.close()
del fil_winsize, data
gc.collect()
