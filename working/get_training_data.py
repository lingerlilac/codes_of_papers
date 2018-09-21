#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
from decimal import *
try:
    fil_winsize = codecs.open("r.txt", "r", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    winsize = csv.reader(fil_winsize)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "winsize_filelist open failed"
    exit()

for i in winsize:
    print i

if fil_winsize:
    fil_winsize.close()
