import os
import pandas as pd
import dpkt
import datetime as dt
import matplotlib.pyplot as plt
import socket


def get_loss_latency_UL_DL(server_UL_file, cell_phone_file): #server_UL_file for UL analysis (same as before); cell_phone_file for DL analysis
    #============================UL part=======================
    
    f = open(server_UL_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    
    timestamp_list = []
    
    for ts, buf in pcap:
    
        #Extract payload of the UDP packet
        #---------------------------------
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.ip       
        udp = ip.data    
        
        if len(udp) == 250+8:       # We set the payload length to be 250 in iperf, so here we set the length checking to be 250 + 8
            #                       #當 packet payload 大小改變時，此大小需要修正

            datetimedec = int(udp.data.hex()[0:8], 16)
            microsec = int(udp.data.hex()[8:16], 16)

            seq = int(udp.data.hex()[16:24], 16)

            if seq == 1:            #可能在做實驗時，會有 iperf3 重新開始的狀況。
                timestamp_list = []

            timestamp_list.append((ts, datetimedec, microsec, seq))

    timestamp_list = sorted(timestamp_list, key = lambda v : v[3])

    pointer = 1
    timestamp_store = None
    loss_timestamp = []

    #Checking packet loss...
    #----------------------------------------------
    for timestamp in timestamp_list:
        if timestamp[3] == pointer:
            timestamp_store = timestamp    
        elif timestamp[3] == pointer - 1:
            print("received duplicated packets", server_UL_file, timestamp[0])
        else:
            for i in range(timestamp[3]-pointer):
                loss_timestamp.append(timestamp_store)
        pointer = timestamp[3] + 1

    UL_loss_time_list = []
    for index, i in zip(range(len(loss_timestamp)), loss_timestamp):
        if i == None:
            continue
        lost_time =  dt.datetime.utcfromtimestamp(i[1] + i[2]/1000000.) + dt.timedelta(seconds=3600*8) #for pcap packets, the timestamps are needed to add 8 hours (timezone)
        UL_loss_time_list.append(lost_time)
    
    #x and y stands for the timestamp (x) and the one-way latency (y) on the timestamp, respectively
    #----------------------------------------------
    x = []
    y = []
    for i in range(len(timestamp_list)):
        transmitted_time = dt.datetime.utcfromtimestamp(timestamp_list[i][1] + timestamp_list[i][2]/1000000.) + dt.timedelta(seconds=3600*8) #for pcap packets, the timestamps are needed to add 8 hours (timezone)
        x.append(transmitted_time)
        y.append( ( timestamp_list[i][0]+3600*8 - (timestamp_list[i][1] + timestamp_list[i][2]/1000000. + 3600*8) ) * 1000 )
    
    UL_latency = [x, y]
    
    #===============================DL part===========================
    f = open(cell_phone_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    timestamp_list = []

    it = 0
    for ts, buf in pcap:
        #print(it)
        it += 1
        
        #print(type(buf), len(buf))  #bytes 298
        eth = dpkt.sll.SLL(buf)
        
        if len(eth.data) == 278:
            
            ip = eth.data
            udp = ip.data
            
            dst_ip_addr_str = socket.inet_ntoa(ip.dst)
            if dst_ip_addr_str == "140.112.20.183":     #UL
                continue
                
            #----------only DL data left---------
            datetimedec = int(udp.data.hex()[0:8], 16)
            microsec = int(udp.data.hex()[8:16], 16)
            seq = int(udp.data.hex()[16:24], 16)
            if seq == 1:
                timestamp_list = []
            timestamp_list.append((ts, datetimedec, microsec, seq))
    

    pointer = 1
    timestamp_store = None
    loss_timestamp = []

    #Checking packet loss...
    #----------------------------------------------
    for timestamp in timestamp_list:
        if timestamp[3] == pointer:
            timestamp_store = timestamp    
        elif timestamp[3] == pointer - 1:
            print("received duplicated packets", server_UL_file, timestamp[0])
        else:
            for i in range(timestamp[3]-pointer):
                loss_timestamp.append(timestamp_store)
        pointer = timestamp[3] + 1

    DL_loss_time_list = []
    for index, i in zip(range(len(loss_timestamp)), loss_timestamp):
        if i == None:
            continue
        lost_time = dt.datetime.utcfromtimestamp(i[0]) + dt.timedelta(hours=8) #for pcap packets, the timestamps are needed to add 8 hours (timezone)
        DL_loss_time_list.append(lost_time)
    
    x = []
    y = []
            
    for i in range(len(timestamp_list)):
        arrival_time = dt.datetime.utcfromtimestamp(timestamp_list[i][0]) + dt.timedelta(seconds=3600*8) #for pcap packets, the timestamps are needed to add 8 hours (timezone) 
        x.append(arrival_time)
        y.append( ( timestamp_list[i][0]+3600*8 - (timestamp_list[i][1] + timestamp_list[i][2]/1000000. + 3600*8) ) * 1000 )

    DL_latency = [x,y]    

    
    return UL_loss_time_list, UL_latency, DL_loss_time_list, DL_latency

   
cell_phone_file = "22-01-16-18-03-28.pcap"
server_UL_file = "32312022-1-16-18-3-21_server_UL.pcap"
server_DL_file = "32322022-1-16-18-3-21_server_DL.pcap"

#simple drawing...
fig , ax = plt.subplots(2, 1, sharex=True, sharey=False)

UL_loss_time_list, UL_latency, DL_loss_time_list, DL_latency = get_loss_latency_UL_DL(server_UL_file, cell_phone_file)

print(len(UL_loss_time_list), len(DL_loss_time_list))

plt.subplot(2,1,1)
plt.plot(UL_latency[0], UL_latency[1], c='blue')
for loss_time in UL_loss_time_list:
    plt.axvline(loss, c='red')

plt.subplot(2,1,2)
plt.plot(DL_latency[0], DL_latency[1], c='blue')
for loss_time in DL_loss_time_list:
    plt.axvline(loss, c='red')

plt.show()