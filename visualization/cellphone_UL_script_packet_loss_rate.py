import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from tqdm import tqdm
import os
import dpkt
import sys
import time


tcpdumpfile = "ok.pcap"
f = open(tcpdumpfile, "rb")
pcap = dpkt.pcap.Reader(f)     

timestamp_list = []

#This for loop parse the payload of the iperf3 UDP packets and store the timestamps and the sequence numbers in timestamp_list; 
#The timestamp is stored in the first 8 bytes, and the sequence number is stored in the 9~12 bytes
#-----------------------------------------------------------------------------------------------

for ts, buf in pcap:

    #Extract payload of the UDP packet
    #---------------------------------
    eth = dpkt.sll.SLL(buf)
                       # duplicate packet       # src == 140.112.20.183
    if (len(eth.data) - 28) % 250  == 0 and eth.data.src == b'\x8cp\x14\xb7':    # We set the payload length to be 250 in iperf, so here we set the length checking to be 250 + (20+8)

        duplicate_num = (len(eth.data) - 28) // 250

        ip = eth.data
        udp = ip.data
        datetimedec = int(udp.data.hex()[0:8], 16)
        microsec = int(udp.data.hex()[8:16], 16)

        seq = int(udp.data.hex()[16:24], 16)
        
        if seq == 1:
            timestamp_list = []
        for i in range(duplicate_num):
            timestamp_list.append((ts, datetimedec, microsec, seq+i))

timestamp_list = sorted(timestamp_list, key = lambda v : v[3])  #We consider out of order UDP packets

pointer = 1
timestamp_store = None
loss_timestamp = []

#Checking packet loss...
#----------------------------------------------
for timestamp in timestamp_list:
    if timestamp[3] == pointer:
        timestamp_store = timestamp    
    else:
        for i in range(timestamp[3]-pointer):
            loss_timestamp.append(timestamp_store)
            
    pointer = timestamp[3] + 1

print("number of packet", len(timestamp_list))
print("number of lost packet", len(loss_timestamp))
print("packet loss rate", len(loss_timestamp) / len(timestamp_list))