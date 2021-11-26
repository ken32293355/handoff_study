"""
Given the device log and iperflog, and this code can do the visulization.
"""

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import os
class Signal_analysis():
    def __init__(self, device_logfilename, iperflogfilename):

        self.df = pd.read_csv(device_logfilename)
        self.iperf_logfile = pd.read_csv(iperflogfilename)
        self.iperf_logfile.Time = pd.to_datetime(self.iperf_logfile.Time).dt.tz_localize(None)

        self.df.loc[:, "Date"] = pd.to_datetime(self.df.loc[:, "Date"])

        ##### You can customize the begin time and end time #####
        # self.begin_time = dt.datetime(2021, 7, 17, 15)
        # self.end_time = dt.datetime(2021, 7, 17, 21)

        self.begin_time = self.iperf_logfile.loc[0, "Time"]
        self.end_time = self.iperf_logfile.loc[self.iperf_logfile.index[-1], "Time"]
        self.iperf_logfile = self.iperf_logfile[(self.begin_time<=self.iperf_logfile.loc[:, "Time"]) & (self.iperf_logfile.loc[:, "Time"]  <= self.end_time)]

        self.df = self.df[(self.begin_time<=self.df.loc[:, "Date"]) & (self.df.loc[:, "Date"]  <= self.end_time)]

        self.df.reset_index(inplace = True)
        self.iperf_logfile.reset_index(inplace = True)


        self.change_time_list = []
        self.pci_list_dict = {}
        self.change_time_5g_list = []
        self.pci_list_5g_dict = {}
        self.MNC = None
        for i in range(len(self.df)):
            if self.df.loc[i, "MNC"] != "0" and self.df.loc[i, "MNC"] != "-":
                self.MNC = self.df.loc[i, "MNC"]
                break

    def show_figure(self):
        prev_PCI = int(self.df.loc[0, "PCI"]) 
        plt.suptitle("UPlink UDP Test")
        plt.suptitle("Downlink UDP Test")
        plt.subplot(511)
        plt.xlim(self.begin_time, self.end_time)

        plt.title("LTE RSRP")
        rsrp_l = []
        time_l = []
        lte_handover_time_l = []
        nr_handover_time_l = []
        prev_earfcn = self.df.loc[0, "earfcn"]
        for i in range(len(self.df)):
            if self.df.loc[i, "MNC"] == self.MNC:
                if prev_PCI != int(self.df.loc[i, "PCI"]):
                    lte_handover_time_l.append(self.df.loc[i, "Date"])
                    plt.scatter(self.df.loc[i, "Date"], self.df.loc[i, "RSRP"], marker="^", c='r')
                    plt.plot(time_l, rsrp_l)
                    rsrp_l = [int(self.df.loc[i, "RSRP"])]
                    time_l = [self.df.loc[i, "Date"] ]
                else:
                    rsrp_l.append(int(self.df.loc[i, "RSRP"]))
                    time_l.append(self.df.loc[i, "Date"])
                
                if prev_earfcn != int (int(self.df.loc[i, "earfcn"])):
                    plt.scatter(self.df.loc[i, "Date"], self.df.loc[i, "RSRP"], marker="o", c='g', label = "band changing")
                    plt.plot(time_l, rsrp_l)
                prev_PCI = int(self.df.loc[i, "PCI"])
                prev_earfcn = int(self.df.loc[i, "earfcn"])
        if len(time_l):
            plt.plot(time_l, rsrp_l)




        plt.ylabel("db")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())


        plt.subplot(512)


        plt.title("NR RSRP")
        rsrp_5g_l = []
        time_l = []
        prev_5g_pci = int(self.df.loc[0, "PCI_5g"])
        for i in range(len(self.df)):
            if self.df.loc[i, "band_5g"] != 0:

                if prev_5g_pci != self.df.loc[i, "PCI_5g"]:
                    nr_handover_time_l.append(self.df.loc[i, "Date"])
                    plt.plot(time_l, rsrp_5g_l)
                    rsrp_5g_l = []
                    time_l = []
                    print(self.df.loc[i, "Date"], self.df.loc[i, "RSRP_5g"])

                    plt.scatter(self.df.loc[i, "Date"], self.df.loc[i, "RSRP_5g"], marker='^', c='orange')
                rsrp_5g_l.append(self.df.loc[i, "RSRP_5g"])
                time_l.append(self.df.loc[i, "Date"])

            elif len(rsrp_5g_l):
                plt.plot(time_l, rsrp_5g_l)
                rsrp_5g_l = []
                time_l = []
            
            prev_5g_pci = self.df.loc[i, "PCI_5g"]


            plt.ylabel("rsrp")
        plt.xlim(self.begin_time, self.end_time)

        plt.subplot(513)


        for x in lte_handover_time_l:
            plt.axvline(x, c = 'r', label = "LTE handover")
        for x in nr_handover_time_l:
            plt.axvline(x, c = 'orange', dash_capstyle='round', label = 'NR handover')

        plt.title("Jitter")
        plt.plot(self.iperf_logfile.loc[:, "Time"], self.iperf_logfile.loc[:, "Jitter"], label = "jitter")
        plt.yscale("log")
        plt.xlim(self.begin_time, self.end_time)


        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())


        plt.ylabel("ms")
        plt.subplot(514)
        plt.title("packet loss rate")


        for x in lte_handover_time_l:
            plt.axvline(x, c = 'r', label = "LTE hand over")
        for x in nr_handover_time_l:
            plt.axvline(x, c = 'orange', dash_capstyle='round', label = 'NR handover')
        plt.plot(self.iperf_logfile.loc[:, "Time"], self.iperf_logfile.loc[:, "Lost_p"], label = "# packet loss")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.xlim(self.begin_time, self.end_time)







        plt.subplot(515)
        plt.title("packet loss")
        plt.yscale("log")


        for x in lte_handover_time_l:
            plt.axvline(x, c = 'r', label = "LTE hand over")
        for x in nr_handover_time_l:
            plt.axvline(x, c = 'orange', dash_capstyle='round', label = 'NR handover')
        plt.plot(self.iperf_logfile.loc[:, "Time"], self.iperf_logfile.loc[:, "Lost"], label = "# packet loss")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.xlim(self.begin_time, self.end_time)




        plt.plot()

        plt.xlim(self.begin_time, self.end_time)




        plt.tight_layout()
        plt.show()


if __name__ == "__main__":

    X = Signal_analysis(device_logfilename = r"log_2021-8-15-21-54-41.csv", iperflogfilename="./log/UL_2021-8-15-21-54-26_server.log.csv")
    X.show_figure()