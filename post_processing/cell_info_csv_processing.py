######csv_processing.py#########
#==============instructions==============
###### This file can process all the cellInfo csv files under a directory.
###### After processing, the csv files can successfully be read by Python pandas 
###### Ex. python csv_processing.py DIRRECTORY_NAME

import os
import sys

dirname = sys.argv[1]
filenames = os.listdir(dirname)

csv_files = []
for filename in filenames:
    if ".csv" in filename:
        csv_files.append(dirname + filename)
        
for csv_file in csv_files:
    f = open(csv_file, 'r')
    lines = f.readlines()
    
    #第一次讀檔案
    max_row_size = 0
    for line in lines:
        row_size = len(line.split(","))
        if row_size > max_row_size:
            max_row_size = row_size
            
    #看原本檔案有沒有 column_names 了
    need_column = 1
    line0 = lines[0]
    if line0[:4] == "Date": #Start with "Date"
        need_column = 0
    
    #第二次讀檔案: 邊讀邊寫
    fnew = open(csv_file[:-4]+"_new.csv", "w")
    print(csv_file[:-4]+"_new.csv")
    
    if need_column:
        column_names = "Date,GPSLat,GPSLon,GPSSpeed,NetLat,NetLon,NetSpeed,RxRate,TxRate,DLBandwidth,ULBandwidth,LTE,LTE_RSRP,LTE_RSRQ,NR,NR_SSRSRP,NR_SSRSRQ,NR_CSIRSRP,NR_CSIRSRQ,Type,MNC,MCC,CID,PCI,SigStrength,earfcn,PCI1,SigStrength1,earfcn1"
        row_size = len(column_names.split(","))
        for i in range(max_row_size - row_size):
            column_names = column_names + ","
        column_names = column_names + '\n'
        fnew.write(column_names)
        
    for line in lines:
        row_size = len(line.split(","))
        append_line = line[:-1]
        for i in range(max_row_size - row_size):
            append_line = append_line + ",-"
        append_line = append_line + "\n"
        fnew.write(append_line)
    f.close()
    fnew.close()
