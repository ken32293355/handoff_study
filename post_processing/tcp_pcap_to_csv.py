from operator import sub
import subprocess
import os
import sys

def pcap_to_csv(infilepath, outfilepath):
    s = "tshark -r %s -T\
fields -e frame.number -e frame.time -e ip.src -e ip.dst\
 -e frame.len -e tcp.analysis.acks_frame -e tcp.len -e tcp.analysis.ack_rtt  -e _ws.col.Info -e tcp.payload -E header=y -E separator=@ >%s"%(infilepath, outfilepath)
#     s = "tshark -r %s -T\
# fields -e frame.number -e frame.time -e ip.src -e ip.dst\
#  -e frame.len -e tcp.analysis.ack_rtt  -e _ws.col.Info  -E header=y -E separator=@ >%s&"%(infilepath, outfilepath)

    print(s)
    subprocess.Popen([s], shell=True)


filename = "/home/wmnlab/D/pcap_data/DL_3242_2022-3-23-10-30-12.pcap"
pcap_to_csv(filename, "/home/wmnlab/D/pcap_csv/" + "DL1-10000.csv")
filename = "/home/wmnlab/D/pcap_data/DL_3246_2022-3-23-10-30-12.pcap"
pcap_to_csv(filename, "/home/wmnlab/D/pcap_csv/" + "DL2-10000.csv")
