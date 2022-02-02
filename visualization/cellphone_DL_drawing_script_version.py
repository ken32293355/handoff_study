######cellphone_DL_script_version.py#########
#==============instructions==============

#!!!!! The get latency correctly, this code requires recompiling the iperf3, modifing the iperf_time_now function in iperf_time.c:
#!!!!! (line 43:) result = clock_gettime(CLOCK_REALTIME, &ts);
#!!!!! Otherwise, the timestamp of the pcap UDP file is not the current time (but is monotone), and you can only compute the jitter and cannot compute the one-way latency.

###### Firstly, to enable Python pandas package to read the csv file, the columns after "earfcn" are needed to be deleted (or places that don't have values are needed to filled in char "-")
#           Make sure that after saving the monitor csv file, the "Date" column are not changed and still have information for "seconds" 
###### Finally, choose the start time and end time (optional)
#           format example: "2021/01/27,15:48:17" 


import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from tqdm import tqdm
import os

import dpkt
import sys

import socket

import matplotlib
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 18}
matplotlib.rc('font', **font)

cellinfo = r".\\"+sys.argv[1] 
tcpdumpfile = ".\\"+sys.argv[2] 

def get_loss_latency(pcap):
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
    
    latency = [x, y]
    
    return loss_timestamp, latency

class Signal_analysis():
    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        
        #self.df.loc[:, "Date"] = pd.to_datetime(self.df.loc[:, "Date"]) 
        #If the above line has bug, comment the line and try this:
        for i in range(len(self.df)):
            self.df.loc[i, "Date"] = dt.datetime.strptime(self.df.loc[i, "Date"], '%m/%d/%y %H:%M:%S ') #10/03/21 21:02:06
       
        self.begin_time = self.df.loc[self.df.index[0], "Date"]
        self.end_time = self.df.loc[self.df.index[-1], "Date"]
        print(self.begin_time)
        
        self.change_time_list = []
        self.cid_list_dict = {}
        self.MNC = None
        for i in range(len(self.df)):
            if self.df.loc[i, "MNC"] != "0" and self.df.loc[i, "MNC"] != "-":
                self.MNC = self.df.loc[i, "MNC"]
       
    def show_figure(self):
        fig , ax = plt.subplots(2, 1, sharex=True, sharey=False)
        
        
        #Start plotting for the upper figure
        #===============================================================================================
        plt.subplot(2,1,1)
        prev_CID = self.df.loc[0, "CID"]
       
        lte_data_x=[]
        lte_data_y=[]
        nr_data_x=[]
        nr_data_y=[]
          
        #This for loop go through the monitor csv file and plot the signal strength for both LTE and NR; 
        #It also plot the LTE handover indicator (red triangle) on the upper figure
        #-----------------------------------------------------------------------------------------------
        for i in range(len(self.df)):
            if self.df.loc[i, "MNC"] != self.MNC:
                print("error: MNC not normal", i, self.MNC, self.df.loc[i, "MNC"])
                
            else:
                if self.df.loc[i, "NR_SSRSRP"] == '-':  #no NR signal
                    plt.plot(nr_data_x, nr_data_y, color="blue")
                    nr_data_x = []
                    nr_data_y = []
                else:
                    nr_data_x.append(self.df.loc[i, "Date"])
                    nr_data_y.append(int(self.df.loc[i, "NR_SSRSRP"]))
                
                if self.df.loc[i, "CID"] != prev_CID:
                    prev_CID = self.df.loc[i, "CID"]
                    plt.plot(lte_data_x, lte_data_y, color="orange")
                    plt.plot(nr_data_x, nr_data_y, color="blue")
                    
                    plt.scatter(self.df.loc[i, "Date"], int(self.df.loc[i, "LTE_RSRP"]), marker = '^', color="red")
                    
                    lte_data_x = []
                    lte_data_y = []
                    nr_data_x = []
                    nr_data_y = []
                
                
                lte_data_x.append(self.df.loc[i, "Date"])
                lte_data_y.append(int(self.df.loc[i, "LTE_RSRP"]))
           
        
        plt.plot(nr_data_x, nr_data_y, color="blue")
        plt.plot(lte_data_x, lte_data_y, color="orange")
        
        #Other setting (label, legend, etc) for the upper figure
        #-----------------------------------------------------------------------------------------------
        import matplotlib.lines as mlines
        blue_line = mlines.Line2D([], [], color='blue', label='NR')
        orange_line = mlines.Line2D([], [], color='orange', label='LTE RSRP')
        plt.legend(handles=[blue_line, orange_line])
        plt.xlabel("UE time")
        plt.ylabel("rsrp")
        
        
        #Start plotting for the upper figure
        #===============================================================================================
        plt.subplot(2,1,2)

        
        f = open(tcpdumpfile, "rb")
        pcap = dpkt.pcap.Reader(f)     

        loss_timestamp, latency = get_loss_latency(pcap)
        [x,y] = latency

        for i in range(len(y)): #there are difference between the time of the cell phone and that of the server; we need to synchronize them
            y[i] = y[i] - int(sys.argv[3])

        #Plot one-way latency and packet loss on the lower figure
        #--------------------------------------------------------
        plt.plot(x, y, color='b', label="latency")
        
        
       
        for index, loss_time in zip(range(len(loss_timestamp)), loss_timestamp):
           
            if index == 0:
                plt.plot([loss_time, loss_time], [sorted(y)[0]-10, sorted(y)[-1]+10], color='r', label="packet loss")    
            else:
                plt.plot([loss_time, loss_time], [sorted(y)[0]-10, sorted(y)[-1]+10], color='r')  
                
        #Other setting for the lower figure
        #--------------------------------------------------------
        plt.legend()        
        plt.xlabel("transmitted time")
        plt.ylim(sorted(y)[0]-10, sorted(y)[-1]+10)
        
        #使上下兩張圖的時間刻度對齊
        #--------------------------------------------------------
        if len(sys.argv) == 4:
            plt.xlim(x[0], x[-1])
        elif len(sys.argv) == 6:
            start_time = pd.to_datetime(sys.argv[4], format='%Y/%m/%d,%H:%M:%S')
            end_time = pd.to_datetime(sys.argv[5], format='%Y/%m/%d,%H:%M:%S')
            plt.xlim(start_time, end_time)

        plt.ylabel("msec")
        plt.subplot(2,1,1)
        if len(sys.argv) == 4:
            plt.xlim(x[0], x[-1])
        elif len(sys.argv) == 6:
            start_time = pd.to_datetime(sys.argv[4], format='%Y/%m/%d,%H:%M:%S')
            end_time = pd.to_datetime(sys.argv[5], format='%Y/%m/%d,%H:%M:%S')
            plt.xlim(start_time, end_time)
        
        
        
        
        plt.show()        
        
        
if __name__ == "__main__":
    X = Signal_analysis(cellinfo)
    X.show_figure()