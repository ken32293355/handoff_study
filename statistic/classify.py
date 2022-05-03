######classify.py#########
#==============instructions==============
###### This python file classifies the packet losses and can save the output as csv file
###### Types of classification:
#           before/during/after eNB handover under 4G
#           before/during/after gNB addition 
#           before/during/after gNB handover
#           before/during/after gNB removal
#           before/during/after eNB handover under 5G (gNB stays the same)
#           before/during/after eNB gNB handover at the same time
#           before/after scg_failure 
#           before/after eNB reestablish request
#           None of above


import os
import pandas as pd
import dpkt
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import intervals as I

dirnames = ["/home/wmnlab/Desktop/tmp"]
mi_files = []
csv_files = []
pcap_files = []

#This for loop extract all the (mi_file, csv_file, pcap_file) items and store them in the lists
#----------------------------------------------------------
for dirname in dirnames:
    filenames = os.listdir(dirname)

    for filename in filenames:
        if ".csv" in filename:
            csv_files.append(dirname + "\\" + filename)
        elif ".pcap" in filename:
            pcap_files.append(dirname + "\\" + filename)
    
    mi_dirname = dirname + "\\diag_txt"
    filenames = os.listdir(mi_dirname)
    for filename in filenames:
        if ".csv" in filename:
            mi_files.append(mi_dirname + "\\" + filename)
            
csv_files = csv_files[:14]
pcap_files = pcap_files[:14]
        
print(len(mi_files), mi_files)
print(len(csv_files), csv_files)
print(len(pcap_files), pcap_files)

#This function parses the tcpdump file which store the UDP iperf packets.
#Then, this function get the timing for packet loss and one-way latency from parsing
#====================================================================================
def get_loss_latency(pcap):
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
        else:
            for i in range(timestamp[3]-pointer):
                loss_timestamp.append(timestamp_store)
        pointer = timestamp[3] + 1

    loss_time_list = []
    for index, i in zip(range(len(loss_timestamp)), loss_timestamp):
        if i == None:
            continue
        lost_time = dt.datetime.utcfromtimestamp(i[0]) + dt.timedelta(hours=8) #for pcap packets, the timestamps are needed to add 8 hours (timezone)
        loss_time_list.append(lost_time)
    
    #x and y stands for the timestamp (x) and the one-way latency (y) on the timestamp, respectively
    #----------------------------------------------
    x = []
    y = []
    for i in range(len(timestamp_list)):
        transmitted_time = dt.datetime.utcfromtimestamp(timestamp_list[i][1] + timestamp_list[i][2]/1000000.) + dt.timedelta(seconds=3600*8) #for pcap packets, the timestamps are needed to add 8 hours (timezone)
        x.append(transmitted_time)
        y.append( ( timestamp_list[i][0]+3600*8 - (timestamp_list[i][1] + timestamp_list[i][2]/1000000. + 3600*8) ) * 1000 )
    
    latency = [x, y]

    return loss_time_list, latency
	
    
#This function parses the mobile insight csv file which is th output file of xml_mi.py 
#Then, this function generates the lists for the event timing
#====================================================================================
def mi_event_parsing(miinfofile, nr_time_intervals):

    nr_pci = None
    
    lte_4G_handover_list = []   #4G 狀態下LTE eNB 的 handover
    
    nr_setup_list = []          #gNB cell addition
    nr_handover_list = []       #gNB cell changes (eNB stays the same)
    nr_removal_list = []        #gNB cell removal
        
    lte_5G_handover_list = []   #(eNB1, gNB1) -> (eNB2, gNB1) #gNB stays the same
    nr_lte_handover_list = []   #both NR cell and LTE cell have handover
    
    scg_failure_list = []       #gNB handover failure
    reestablish_list = []       #eNB handover failure
    
    nr_handover = 0
    nr_handover_start_index = None
    lte_handover = 0
    lte_handover_start_index = None
    nr_release = 0
    nr_release_start_index = None
    
    handover_num = 0
    
    #initialization
    #----------------------------------------------------------------
    if miinfofile.loc[0, "time"] in nr_time_intervals:
        nr_pci = 1000000            #先設置一個數 dummy nr pci
    
    for i in range(len(miinfofile)):       
        if miinfofile.loc[i, "nr-rrc.t304"]:
            if nr_handover == 0:    
                nr_handover = 1
                nr_handover_start_index = i
                
        if miinfofile.loc[i, "lte-rrc.t304"]:
            if lte_handover == 0:
                lte_handover = 1
                lte_handover_start_index = i
                
        if miinfofile.loc[i, "nr-Config-r15: release (0)"]:
            if nr_release == 0:
                nr_release = 1
                nr_release_start_index = i
           
        if (nr_handover or lte_handover or nr_release) and miinfofile.loc[i, "rrcConnectionReconfigurationComplete"]:
            handover_num +=1
        
        
        #handover 種類分類
        #------------------------------------------------------------------------------
        if lte_handover and not nr_handover and miinfofile.loc[i, "rrcConnectionReconfigurationComplete"]:  # just lte cell handover event
            lte_handover = 0
            lte_4G_handover_list.append([miinfofile.loc[lte_handover_start_index, "time"], miinfofile.loc[i, "time"]])
            
        if nr_handover and not lte_handover and miinfofile.loc[i, "rrcConnectionReconfigurationComplete"]:  # just nr cell handover event
            nr_handover = 0
            if miinfofile.loc[nr_handover_start_index, "dualConnectivityPHR: setup (1)"]:     #This if-else statement classifies whether it is nr addition or nr handover
                nr_setup_list.append([miinfofile.loc[nr_handover_start_index, "time"], miinfofile.loc[i, "time"]])       
            else:
                nr_handover_list.append([miinfofile.loc[nr_handover_start_index, "time"], miinfofile.loc[i, "time"]])
                
            #additional judgement:
            #----------------------------
            #if miinfofile.loc[nr_handover_start_index, "dualConnectivityPHR: setup (1)"] and nr_pci != None:
            #    print("Warning: dualConnectivityPHR setup may not mean nr cell addition", mi_file, i)
            #if miinfofile.loc[nr_handover_start_index, "dualConnectivityPHR: setup (1)"]==0 and not (nr_pci != None and nr_pci != miinfofile.loc[nr_handover_start_index, "nr_pci"]): 
            #    print("Warning: nr-rrc.t304 without dualConnectivityPHR setup may not mean nr cell handover", mi_file, i, nr_handover_start_index, miinfofile.loc[nr_handover_start_index, "nr_pci"], nr_pci)
                
            #nr_pci update lte_handover_start_time
            nr_pci = miinfofile.loc[nr_handover_start_index, "nr_pci"]
            
            
        if lte_handover and nr_handover and miinfofile.loc[i, "rrcConnectionReconfigurationComplete"]:      # both nr cell and lte cell handover event
            lte_handover = 0
            nr_handover = 0
            if nr_pci == miinfofile.loc[lte_handover_start_index, "nr_pci"]:
                lte_5G_handover_list.append([miinfofile.loc[lte_handover_start_index, "time"], miinfofile.loc[i, "time"]])
            else:
                nr_lte_handover_list.append([miinfofile.loc[lte_handover_start_index, "time"], miinfofile.loc[i, "time"]])
            
            #nr_pci update
            nr_pci = miinfofile.loc[lte_handover_start_index, "nr_pci"]
            
        if nr_release and miinfofile.loc[i, "rrcConnectionReconfigurationComplete"]:
            nr_pci = None
            nr_release=0
            nr_removal_list.append([miinfofile.loc[nr_release_start_index, "time"], miinfofile.loc[i, "time"]])
        if miinfofile.loc[i, "scgFailureInformationNR-r15"]:
            scg_failure_list.append([miinfofile.loc[i, "time"], miinfofile.loc[i, "time"]])
        if miinfofile.loc[i, "rrcConnectionReestablishmentRequest"]:
            reestablish_list.append([miinfofile.loc[i, "time"], miinfofile.loc[i, "time"]])
            
    return [lte_4G_handover_list, nr_setup_list, nr_handover_list, nr_removal_list, lte_5G_handover_list, nr_lte_handover_list, scg_failure_list, reestablish_list], handover_num

#This function firstly generates three intervals for each [handover_start, handover_end] in handover_list
#   a. before the handover_start event: [handover_start-second, handover_start]
#   b. during the handover events: [handover_start, handover_end]
#   c. after the handover_end event: [handover_end, handover_end+second]
#Then, it returns the overall intervals before/during/after the handover event
#--------------------------------------------------------------------
def get_before_during_after_intervals(handover_list, second):
    before_handover_intervals = I.empty()
    handover_intervals = I.empty()
    after_handover_intervals = I.empty()
    for i in range(len(handover_list)):  
        interval = I.closed( handover_list[i][0]-dt.timedelta(seconds=second), handover_list[i][0] )
        before_handover_intervals = before_handover_intervals | interval
        
        interval = I.closed( handover_list[i][0], handover_list[i][1] )
        handover_intervals = handover_intervals | interval
        
        interval = I.closed( handover_list[i][1], handover_list[i][1]+dt.timedelta(seconds=second) )
        after_handover_intervals = after_handover_intervals | interval    
    return before_handover_intervals, handover_intervals, after_handover_intervals
   
#This function returns the overall length of the intervals
#--------------------------------------------------------------------
def get_sum_intervals(intervals):
    if intervals.is_empty():
        return 0
    sum = 0
    for x in intervals:
        sum += (x.upper - x.lower)/dt.timedelta(seconds=1)
    return sum
    
event_names = [
    "lte_4G_handover",
    "nr_setup",
    "nr_handover",
    "nr_removal",
    "lte_5G_handover",
    "nr_lte_handover_list",
    "scg_failure",
    "reestablish"
]

column_names = []

for i in range(len(event_names)-2):
    column_names += ["before_"+event_names[i]+"_intervals", "during_"+event_names[i]+"_intervals", "after_"+event_names[i]+"_intervals"]
for i in range(len(event_names)-2, len(event_names)):
    column_names += ["before_"+event_names[i]+"_intervals", "after_"+event_names[i]+"_intervals"]
    
column_names += ["nr_time_intervals", "weak_nr_intervals", "weak_lte_intervals"]
print("column_names=", column_names)

sum_intervals = [0] * len(column_names)
sum_packet_loss = [0] * len(column_names)
sum_stable_intervals = 0
        
for csv_file, pcap_file, mi_file in zip(csv_files, pcap_files, mi_files):
    f = open(pcap_file, "rb")
    pcap = dpkt.pcap.Reader(f)

    cellinfofile = pd.read_csv(csv_file)
    cellinfofile.loc[:, "Date"] = pd.to_datetime(cellinfofile.loc[:, "Date"])
    
    miinfofile = pd.read_csv(mi_file)
    miinfofile.loc[:, "time"] = pd.to_datetime(miinfofile.loc[:, "time"]) + dt.timedelta(hours=8)
    
    #======================lost time (and latency)=============================
    loss_time, latency = get_loss_latency(pcap)
       
    #======================before mi event parse, parse NR intervals first=====
    nr_time_intervals = I.empty()
    if cellinfofile.loc[0, "NR_SSRSRP"] != "-":
        nr_time_intervals = I.singleton(cellinfofile.loc[0, "Date"])
    for i in range(1, len(cellinfofile)):
        if cellinfofile.loc[i, "NR_SSRSRP"] != "-":
            nr_time_intervals = nr_time_intervals | I.openclosed(cellinfofile.loc[i-1, "Date"] , cellinfofile.loc[i, "Date"])
    weak_nr_intervals = I.empty()
    if cellinfofile.loc[0, "NR_SSRSRP"] != "-" and int(cellinfofile.loc[0, "NR_SSRSRP"]) <= -90:
        weak_nr_intervals = I.singleton(cellinfofile.loc[0, "Date"])
    for i in range(1, len(cellinfofile)):
        if cellinfofile.loc[i, "NR_SSRSRP"] != "-" and int(cellinfofile.loc[i, "NR_SSRSRP"]) <= -90:
            weak_nr_intervals = weak_nr_intervals | I.openclosed(cellinfofile.loc[i-1, "Date"] , cellinfofile.loc[i, "Date"])
    weak_lte_intervals = I.empty()
    if cellinfofile.loc[0, "LTE_RSRP"] != "-" and int(cellinfofile.loc[0, "LTE_RSRP"]) <= -90:
        weak_lte_intervals = I.singleton(cellinfofile.loc[0, "Date"])
    for i in range(1, len(cellinfofile)):
        if cellinfofile.loc[i, "LTE_RSRP"] != "-" and int(cellinfofile.loc[i, "LTE_RSRP"]) <= -90:
            weak_lte_intervals = weak_lte_intervals | I.openclosed(cellinfofile.loc[i-1, "Date"] , cellinfofile.loc[i, "Date"])
    
    #======================mi event parse======================================  
    handover_event_lists, handover_num = mi_event_parsing(miinfofile, nr_time_intervals)
    
    #======================making intervals====================================
    intervals = []
    
    for handover_event_list in handover_event_lists[:-2]:
        before_intervals, during_intervals, after_intervals = get_before_during_after_intervals(handover_event_list, 1)     #抓取前後一秒
        intervals += [before_intervals, during_intervals, after_intervals].copy()
    for handover_event_list in handover_event_lists[-2:]:
        before_intervals, _, after_intervals = get_before_during_after_intervals(handover_event_list, 3)                    #抓取前後三秒
        intervals += [before_intervals, after_intervals].copy()    
    
    intervals += [nr_time_intervals, weak_nr_intervals, weak_lte_intervals]
    #================================judgement=================================
    out = pd.DataFrame(columns = column_names, dtype=object)

    #------check time-------
    start_time = miinfofile.loc[0, "time"]
    if cellinfofile.loc[0, "Date"] > start_time:
        start_time = cellinfofile.loc[0, "Date"]
    if latency[0][0] > start_time:
        start_time = latency[0][0]
    end_time = miinfofile.loc[len(miinfofile)-1, "time"]
    if cellinfofile.loc[len(cellinfofile)-1, "Date"] < end_time:
        end_time = cellinfofile.loc[len(cellinfofile)-1, "Date"]
    if latency[0][-1] < end_time:
        end_time = latency[0][-1]
        
    #This for loop check whether each packet loss are in handover event intervals
    #------------------------------------------------------
    for loss_index in range(len(loss_time)):    
        if loss_time[loss_index] < start_time:
            continue
        if loss_time[loss_index] > end_time:
            continue
        
        types = [0]*len(intervals)
        for i in range(len(intervals)):
            if loss_time[loss_index] in intervals[i]:
                types[i] = 1
        out.loc[loss_index] = types                
    
    #output: number of packet loss, number of packet loss under each type, handover num, overall experiment time, file names 
    output = [len(out)] + [len(out.loc[ out[column_names[i]]==1 ]) for i in range(len(column_names)-3)] + [handover_num, (end_time-start_time)/dt.timedelta(seconds=1), csv_file, mi_file, pcap_file]
    print(output)
    
    for i in range(len(column_names)):
        intervals[i] = intervals[i] & I.closed(start_time, end_time)
        sum_intervals[i] += get_sum_intervals(intervals[i])
        
    stable_intervals = I.closed(start_time, end_time)
    for i in range(len(column_names)-3):
        stable_intervals = stable_intervals - intervals[i]
    sum_stable_intervals += get_sum_intervals(stable_intervals)
    
    for i in range(len(column_names)-3):
        sum_packet_loss[i] += len(out.loc[ out[column_names[i]]==1 ])
    
    #User can decide whether save the packet loss classification as csv file
    out.to_csv("all_loss_classify_7.csv", mode='a')

print(sum_stable_intervals)
print([sum_intervals[i] for i in range(len(column_names)-3)])
print([sum_packet_loss[i]/(sum_intervals[i]) for i in range(len(column_names)-3)])