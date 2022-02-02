import os
import pandas as pd
import dpkt
import datetime as dt
import matplotlib.pyplot as plt
import socket

def get_loss_latency_UL(pcap):
    timestamp_list = []

    #This for loop parse the payload of the iperf3 UDP packets and store the timestamps and the sequence numbers in timestamp_list; 
    #The timestamp is stored in the first 8 bytes, and the sequence number is stored in the 9~12 bytes
    #-----------------------------------------------------------------------------------------------
   
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

def get_loss_latency_DL(pcap):
    timestamp_list = []

    #This for loop parse the payload of the iperf3 UDP packets and store the timestamps and the sequence numbers in timestamp_list; 
    #The timestamp is stored in the first 8 bytes, and the sequence number is stored in the 9~12 bytes
    #-----------------------------------------------------------------------------------------------
   
    for ts, buf in pcap:

        #Extract payload of the UDP packet
        #---------------------------------
        eth = dpkt.sll.SLL(buf)  
        
        if (len(eth.data) - (20+8)) % 250 == 0:    # We set the payload length to be 250 in iperf, so here we set the length checking to be 250 + (4+20+8)
            
            ip = eth.data
            udp = ip.data
            
            dst_ip_addr_str = socket.inet_ntoa(ip.dst)
            if dst_ip_addr_str == "140.112.20.183":
                continue
            
            #------------only DL data left--------------
            #bug fix: duplicate packets | credit: JingYou
            duplicate_num = (len(eth.data) - (20+8)) // 250
            
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
            if timestamp_store == None:
                continue
            loss_linspace = np.linspace(timestamp_store, timestamp, timestamp[3]-pointer+2)
            
            for i in loss_linspace:
                loss_time = dt.datetime.utcfromtimestamp(i[0]) + dt.timedelta(hours=8)
                loss_timestamp.append(loss_time)
                
        pointer = timestamp[3] + 1
        
    #x and y stands for the timestamp (x) and the one-way latency (y) on the timestamp, respectively
    #----------------------------------------------
    x = []
    y = []
    
    for i in range(len(timestamp_list)):
        arrival_time = dt.datetime.utcfromtimestamp(timestamp_list[i][0]) + dt.timedelta(seconds=3600*8) #for pcap packets, the timestamps are needed to add 8 hours (timezone) 
        x.append(arrival_time)
        
        y.append( ( timestamp_list[i][0]+3600*8 - (timestamp_list[i][1] + timestamp_list[i][2]/1000000. + 3600*8) ) * 1000 )
    
    print("number of packet", len(timestamp_list))
    print("number of lost packet", len(loss_timestamp))
    if len(timestamp_list):
        print("packet loss rate", len(loss_timestamp) / len(timestamp_list))
    
    return loss_timestamp, [x,y]

   
cell_phone_file = "testing files\\22-01-16-18-03-28.pcap"
server_UL_file = "testing files\\32312022-1-16-18-3-21_server_UL.pcap"
server_DL_file = "testing files\\32322022-1-16-18-3-21_server_DL.pcap"

#simple drawing...
fig , ax = plt.subplots(2, 1, sharex=True, sharey=False)

f = open(server_UL_file, "rb")
pcap = dpkt.pcap.Reader(f)
UL_loss_timestamp, UL_latency = get_loss_latency_UL(pcap)

f = open(cell_phone_file, "rb")
pcap = dpkt.pcap.Reader(f)
DL_loss_timestamp, DL_latency = get_loss_latency_DL(pcap)

print(len(UL_loss_timestamp), len(DL_loss_timestamp))

plt.subplot(2,1,1)
plt.plot(UL_latency[0], UL_latency[1], c='blue')
for loss_time in UL_loss_timestamp:
    plt.axvline(loss_time, c='red')

plt.subplot(2,1,2)
plt.plot(DL_latency[0], DL_latency[1], c='blue')
for loss_time in DL_loss_timestamp:
    plt.axvline(loss_time, c='red')

plt.show()