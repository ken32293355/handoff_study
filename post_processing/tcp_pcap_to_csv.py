from operator import sub
import subprocess
import os
import sys

def pcap_to_csv(infilepath, outfilepath):
    s = "tshark -r %s -T\
fields -e frame.number -e frame.time -e ip.src -e ip.dst\
 -e frame.len -e tcp.analysis.acks_frame  -e tcp.len -e tcp.analysis.ack_rtt  -e _ws.col.Info -e tcp.payload -E header=y -E separator=@ >%s"%(infilepath, outfilepath)

    print(s)
    subprocess.Popen([s], shell=True)


filename = "/home/wmnlab/D/xm14/2022-4-6-18-34-48.pcap"
pcap_to_csv(filename, "/home/wmnlab/D/pcap_csv/" + "UE_0406.csv")

filename = "/home/wmnlab/D/pcap_data2/DL_3257_2022-4-6-18-19-55.pcap"
pcap_to_csv(filename, "/home/wmnlab/D/pcap_csv/" + "DL_0406.csv")

filename = "/home/wmnlab/D/pcap_data2/UL_3267_2022-4-6-18-19-55.pcap"
pcap_to_csv(filename, "/home/wmnlab/D/pcap_csv/" + "UL_0406.csv")
