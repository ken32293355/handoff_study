import os
import pandas as pd
import dpkt
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import intervals as I
import sys

all_exp_dir_names = ["0128 brown line/", "0127 afternoon/", "0127 morning/"]
cell_names = ["xm1 (3231 3232)/", "xm2 (3233 3234)/", "xm3 (3235 3236)/"]

all_file_dir = []
for all_exp_dir_name in all_exp_dir_names:
    for cell_name in cell_names:
        all_file_dir.append(all_exp_dir_name + cell_name)
        print(all_exp_dir_name + cell_name)

all_groups = []
all_group_time = []

for dirname in all_file_dir:
    mi_files = []
    csv_files = []
    cell_phone_pcap_files = []
    UL_pcap_files = []


    filenames = os.listdir(dirname)

    for filename in filenames:
        if '_new.csv' in filename:
            csv_files.append(filename)
        if '.pcap' in filename:
            cell_phone_pcap_files.append(filename)

    UL_dirname = dirname + 'UL/'
    filenames = os.listdir(UL_dirname)
    for filename in filenames:
        if '.pcap' in filename:
            UL_pcap_files.append('UL/'+filename)
            
    diag_dirname = dirname + 'diag_txt/'
    filenames = os.listdir(diag_dirname)
    for filename in filenames:
        if '.csv' in filename:
            mi_files.append('diag_txt/'+filename)
            
    print(len(mi_files), mi_files)
    print(len(csv_files), csv_files)
    print(len(cell_phone_pcap_files), cell_phone_pcap_files)
    print(len(UL_pcap_files), UL_pcap_files)

    grouping = []
    interval = []
    for csv_file in csv_files:
        grouping.append([dirname+csv_file])
        
        cellinfofile = pd.read_csv(dirname + csv_file)
        cellinfofile.loc[:, "Date"] = pd.to_datetime(cellinfofile.loc[:, "Date"])
        interval.append(I.closed(cellinfofile.loc[0,"Date"], cellinfofile.loc[len(cellinfofile)-1,"Date"]))
        

    #=====================UL pcap=====================    
    def get_loss_latency(pcap):
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
        
    store_interval = []
    for UL_pcap_file in UL_pcap_files:
        f = open(dirname + UL_pcap_file, "rb")
        pcap = dpkt.pcap.Reader(f)
        try:
            _, latency = get_loss_latency(pcap)
            store_interval.append(I.closed(latency[0][0],latency[0][-1]))    
        except:
            store_interval.append(I.empty())
            continue
            
    for i in range(len(interval)):
        each_interval = interval[i]
        max_overlap = 0
        max_store_interval_index = None
        for each_store_interval_index in range(len(store_interval)):
            overlap = each_interval & store_interval[each_store_interval_index]
            
            if overlap != I.empty() and (overlap.upper - overlap.lower)//dt.timedelta(seconds=1) > max_overlap:
                max_overlap = (overlap.upper - overlap.lower)//dt.timedelta(seconds=1)
                max_store_interval_index = each_store_interval_index
        
        if max_overlap == 0:
            grouping[i].append("None")
            interval[i] = I.empty()
        else:
            grouping[i].append(dirname+UL_pcap_files[max_store_interval_index])
            interval[i] = interval[i] & store_interval[max_store_interval_index]
     
    #=====================mobile insight=====================  
    store_interval = []
    for mi_file in mi_files:
        miinfofile = pd.read_csv(dirname + mi_file)
        miinfofile.loc[:, "time"] = pd.to_datetime(miinfofile.loc[:, "time"]) + dt.timedelta(hours=8)
        store_interval.append(I.closed(miinfofile.loc[0, "time"], miinfofile.loc[len(miinfofile)-1, "time"]))
     
    for i in range(len(interval)):
        each_interval = interval[i]
        max_overlap = 0
        max_store_interval_index = None
        for each_store_interval_index in range(len(store_interval)):
            overlap = each_interval & store_interval[each_store_interval_index]
            
            if overlap != I.empty() and (overlap.upper - overlap.lower)//dt.timedelta(seconds=1) > max_overlap:
                max_overlap = (overlap.upper - overlap.lower)//dt.timedelta(seconds=1)
                max_store_interval_index = each_store_interval_index
        print(max_overlap)    
        if max_overlap == 0:
            grouping[i].append("None")
            interval[i] = I.empty()
        else:
            grouping[i].append(dirname+mi_files[max_store_interval_index])
            interval[i] = interval[i] & store_interval[max_store_interval_index]
        
    print("grouping")
    for each_group, each_group_time in zip(grouping, interval):
        #print(each_group)
        if each_group[0] != "None" and each_group[1] != "None" and each_group[2] != "None":
            all_groups.append(each_group)
            all_group_time.append(each_group_time)
            
print("===============result===============")
for each_group, each_group_time in zip(all_groups, all_group_time):
    print(each_group, ", sec = ", (each_group_time.upper - each_group_time.lower) // dt.timedelta(seconds=1))
print(len(all_groups))
print(all_groups)
