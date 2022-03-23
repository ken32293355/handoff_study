import datetime as dt
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time


def rtt_plot(pcap_csv):
    df = pd.read_csv(pcap_csv, sep='@')
    df.loc[:, "frame.time"] = pd.to_datetime(df.loc[:, r"frame.time"]).dt.tz_localize(None)
    df = df[np.invert(np.isnan(df.loc[:, "tcp.analysis.ack_rtt"]))]
    df.reset_index(inplace=True)
    # df.plot(df.loc[:, "frame.time"], df.loc[:, "tcp.analysis.ack_rtt"])
    # plt.show()
    plt.xlabel("time")
    plt.ylabel("second")
    plt.plot(df.loc[:, "frame.time"], df.loc[:, "tcp.analysis.ack_rtt"])
    plt.show()

def rtt(pcap_csv):
    df = pd.read_csv(pcap_csv, sep='@')
    df.loc[:, "frame.time"] = pd.to_datetime(df.loc[:, r"frame.time"]).dt.tz_localize(None)
    lenthset = set(df.loc[:, "tcp.len"])
    print(lenthset)
pcap_csv = "/home/wmnlab/D/pcap_csv/" + "DL1-10000.csv"
rtt(pcap_csv=pcap_csv)
