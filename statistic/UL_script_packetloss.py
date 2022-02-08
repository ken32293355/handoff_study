import os
import pandas as pd
import dpkt
import datetime as dt
import matplotlib.pyplot as plt
import socket
import numpy as np
def get_loss_latency_UL(pcapfilename):

    f = open(pcapfilename, "rb")
    pcap = dpkt.pcap.Reader(f)


    timestamp_list = []

    #This for loop parse the payload of the iperf3 UDP packets and store the timestamps and the sequence numbers in timestamp_list; 
    #The timestamp is stored in the first 8 bytes, and the sequence number is stored in the 9~12 bytes
    #-----------------------------------------------------------------------------------------------
    seq_set = set()
   
    for ts, buf in pcap:
        if len(buf) != 292:
            continue
            
        #Extract payload of the UDP packet
        #---------------------------------
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.ip         
        udp = ip.data     
        
        if len(udp) == 250+8:    # We set the payload length to be 250 in iperf, so here we set the length checking to be 250 + 8 
            
            datetimedec = int(udp.data.hex()[0:8], 16)
            microsec = int(udp.data.hex()[8:16], 16)

            seq = int(udp.data.hex()[16:24], 16)
            
            if seq == 1:
                timestamp_list = []
            if seq not in seq_set:              
                seq_set.add(seq)
                timestamp_list.append((ts, datetimedec, microsec, seq))
           
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
            if timestamp_store == None:
                continue
            loss_linspace = np.linspace(timestamp_store, timestamp, timestamp[3]-pointer+2)
                
            for i in loss_linspace:
                loss_time = dt.datetime.utcfromtimestamp(i[1]+i[2]/1000000.) + dt.timedelta(hours=8)
                loss_timestamp.append(loss_time)
                
        pointer = timestamp[3] + 1
        
    #x and y stands for the timestamp (x) and the one-way latency (y) on the timestamp, respectively
    #----------------------------------------------
    x = []
    y = []
    
    for i in range(len(timestamp_list)):
        transmitted_time = dt.datetime.utcfromtimestamp(timestamp_list[i][1] + timestamp_list[i][2]/1000000.) + dt.timedelta(seconds=3600*8) #for pcap packets, the timestamps are needed to add 8 hours (timezone) 
        x.append(transmitted_time)
        
        y.append( ( timestamp_list[i][0]+3600*8 - (timestamp_list[i][1] + timestamp_list[i][2]/1000000. + 3600*8) ) * 1000 )
    
    latency = [x,y]
    
    return loss_timestamp, latency




pcap_filename = r"C:\Users\USER\Desktop\0205data\ss1\round1_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss1\round2_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss1\round3_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss1\round4_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss1\round5_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))

# print("---")

pcap_filename = r"C:\Users\USER\Desktop\0205data\ss2\round1_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss2\round2_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss2\round3_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss2\round4_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
pcap_filename = r"C:\Users\USER\Desktop\0205data\ss2\round5_UL.pcap"
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap_filename)
print(len(UL_latency[0]), len(UL_loss_timestamp), len(UL_loss_timestamp) / len(UL_latency[0]))
