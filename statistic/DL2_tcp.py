import datetime as dt
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time


def rtt_plot(pcap_csv1, pcap_csv2):
    df1 = pd.read_csv(pcap_csv1, sep='@')
    df1.loc[:, "frame.time"] = pd.to_datetime(df1.loc[:, r"frame.time"]).dt.tz_localize(None)
    df1 = df1[np.invert(np.isnan(df1.loc[:, "tcp.analysis.ack_rtt"]))]
    df1.reset_index(inplace=True)

    df2 = pd.read_csv(pcap_csv2, sep='@')
    df2.loc[:, "frame.time"] = pd.to_datetime(df2.loc[:, r"frame.time"]).dt.tz_localize(None)
    df2 = df2[np.invert(np.isnan(df2.loc[:, "tcp.analysis.ack_rtt"]))]
    df2.reset_index(inplace=True)



    print(df1.loc[:, "frame.time"])
    print(df1.loc[:, "tcp.analysis.ack_rtt"])
    plt.plot(df1.loc[:, "frame.time"], df1.loc[:, "tcp.analysis.ack_rtt"])
    plt.plot(df2.loc[:, "frame.time"], df2.loc[:, "tcp.analysis.ack_rtt"])
    plt.show()

    
pcap_csv = "/home/wmnlab/D/pcap_csv/" + "DL1-10000.csv"
pcap_csv2 = "/home/wmnlab/D/pcap_csv/" + "DL2.10000csv"
rtt_plot(pcap_csv1=pcap_csv, pcap_csv2=pcap_csv2)