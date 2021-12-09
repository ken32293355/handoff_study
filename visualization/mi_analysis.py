import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

class Signal:
    def __init__(self, mifile, iperffile, cellinfofile):
        self.mifile = pd.read_csv(mifile)
        self.mifile.loc[:, "time"] = pd.to_datetime(self.mifile.loc[:, "time"]) + dt.timedelta(hours=8)

        self.iperffile = pd.read_csv(iperffile)
        self.iperffile.loc[:, "Time"] = pd.to_datetime(self.iperffile.loc[:, "Time"])


        self.cellinfofile = pd.read_csv(cellinfofile)
        self.cellinfofile.loc[:, "Date"] = pd.to_datetime(self.cellinfofile.loc[:, "Date"])




        self.begin_time = self.iperffile.loc[0, "Time"]
        self.end_time = self.iperffile.loc[self.iperffile.index[-1], "Time"]


        self.mifile = self.mifile[(self.begin_time<=self.mifile.loc[:, "time"]) & (self.mifile.loc[:, "time"]  <= self.end_time)]
        self.cellinfofile = self.cellinfofile[(self.begin_time<=self.cellinfofile.loc[:, "Date"]) & (self.cellinfofile.loc[:, "Date"]  <= self.end_time)]
        
        self.mifile.reset_index(inplace = True)
        self.iperffile.reset_index(inplace = True)
        self.cellinfofile.reset_index(inplace = True)



        print(self.cellinfofile.loc[:, "Date"])
    def show_figure(self):

        plt.title("LTE RSRP")
        plt.subplot(411)
        plt.title("LTE RSRP")
        rsrp_l = []
        time_l = []
        lte_handover_time_l = []
        nr_handover_time_l = []
        prev_earfcn = self.cellinfofile.loc[0, "earfcn"]
        prev_PCI = self.cellinfofile.loc[0, "PCI"]
        for i in range(len(self.cellinfofile)):
            if prev_PCI != int(self.cellinfofile.loc[i, "PCI"]):
                lte_handover_time_l.append(self.cellinfofile.loc[i, "Date"])
                # print(self.cellinfofile.loc[i, "Date"])
                plt.scatter(self.cellinfofile.loc[i, "Date"], self.cellinfofile.loc[i, "LTE_RSRP"], marker="^", c='r', label = "handover")
                plt.plot(time_l, rsrp_l)
                rsrp_l = [int(self.cellinfofile.loc[i, "LTE_RSRP"])]
                time_l = [self.cellinfofile.loc[i, "Date"] ]
            else:
                rsrp_l.append(int(self.cellinfofile.loc[i, "LTE_RSRP"]))
                time_l.append(self.cellinfofile.loc[i, "Date"])
            
            if prev_earfcn != int (int(self.cellinfofile.loc[i, "earfcn"])):
                plt.scatter(self.cellinfofile.loc[i, "Date"], self.cellinfofile.loc[i, "LTE_RSRP"], marker="o", c='g', label = "band changing")
                plt.plot(time_l, rsrp_l)
            prev_PCI = int(self.cellinfofile.loc[i, "PCI"])
            prev_earfcn = int(self.cellinfofile.loc[i, "earfcn"])
        if len(time_l):
            plt.plot(time_l, rsrp_l)


        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.xlim(self.begin_time, self.end_time)
        # plt.legend(by_label.values(), by_label.keys())

        plt.subplot(412)
        plt.title("NR RSRP")
        for i in range(len(self.cellinfofile)):
            if self.cellinfofile.loc[i, "NR_SSRSRP"] == 0 and len(rsrp_l):
                plt.plot(time_l, rsrp_l)
                rsrp_l = []
                time_l = []
            elif self.cellinfofile.loc[i, "NR_SSRSRP"] != 0:
                rsrp_l.append(int(self.cellinfofile.loc[i, "NR_SSRSRP"]))
                time_l.append(self.cellinfofile.loc[i, "Date"])
        if len(time_l):
            plt.plot(time_l, rsrp_l)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        # plt.legend()

        plt.xlim(self.begin_time, self.end_time)
        plt.subplot(413)
        plt.title("packet loss rate")
        plt.plot(self.iperffile.loc[:, "Time"], self.iperffile.loc[:, "Lost_p"])


        c1 = plt.cm.get_cmap('gist_rainbow', 6)(0)
        c2 = plt.cm.get_cmap('gist_rainbow', 6)(1)
        c3 = plt.cm.get_cmap('gist_rainbow', 6)(2)
        c4 = plt.cm.get_cmap('gist_rainbow', 6)(3)
        c5 = plt.cm.get_cmap('gist_rainbow', 6)(4)

        k = 0

        for i in range(len(self.mifile)):
            # if self.mifile.loc[i, "rrcConnectionReconfigurationComplete"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'r', label = "rrcConnectionReconfigurationComplete")

            # if self.mifile.loc[i, "rrcConnectionReconfiguration"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'b', label = "rrcConnectionReconfiguration")


            # if self.mifile.loc[i, "EMM_STATE"] == "EMM_REGISTERED":
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'r', label = "EMM_REGISTERED")

            # if self.mifile.loc[i, "EMM_STATE"] == "EMM_SERVICE_REQUEST_INITIATED":
            #     print("e", self.mifile.loc[i, "time"])
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'r', label = "EMM_SERVICE_REQUEST_INITIATED")

            # if self.mifile.loc[i, "EMM_STATE"] == "EMM_TRACKING_AREA_UPDATING_INITIATED":
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'y', label = "EMM_TRACKING_AREA_UPDATING_INITIATED")
# CellGroupConfig
            if self.mifile.loc[i, "msg3-transformPrecoder"]:
                print(self.mifile.loc[i, "time"])
                plt.axvline(self.mifile.loc[i, "time"], c = c2, label = "msg3-transformPrecoder")

            if self.mifile.loc[i, "nr-rrc.t304"]:
                plt.axvline(self.mifile.loc[i, "time"], c = c4, label = "nr-rrc.t304")

            if self.mifile.loc[i, "lte-rrc.t304"]:
                plt.axvline(self.mifile.loc[i, "time"], c = c5, label = "lte-rrc.t304")


            # if self.mifile.loc[i, "rrcConnectionReestablishmentRequest"]:
            #     j = i
            #     while self.iperffile.loc[k, "Time"] < self.mifile.loc[i, "time"]:
            #         k+=1
            #     while not (self.mifile.loc[j, "rrcConnectionReconfiguration"] == 1 and self.mifile.loc[j, "type_id"] == "LTE_RRC_OTA_Packet"):
            #         j -= 1
            #     # print("type1: ", self.mifile.loc[i, "time"] - self.mifile.loc[j, "time"])
            #     plt.axvline(self.mifile.loc[i, "time"], c = c1, label = "rrcConnectionReestablishmentRequest")
            #     # plt.scatter(self.iperffile.loc[k, "Time"], self.iperffile.loc[k, "Lost_p"], marker="^", c='r', label = "rrcConnectionReestablishmentRequest")

            # if self.mifile.loc[i, r"nr-rrc.RRCReconfigurationComplete_element"]:
            #     j = i
            #     while self.iperffile.loc[k, "Time"] < self.mifile.loc[i, "time"]:
            #         k+=1
            #     while not (self.mifile.loc[j, "t304"] == 1):
            #         j -= 1
            #     # print("handoff time:", self.mifile.loc[i, "time"] - self.mifile.loc[j, "time"], self.mifile.loc[i, "time"], self.mifile.loc[j, "time"])
            #     # plt.axvline(self.mifile.loc[i, "time"], c = c1, label = "rrcConnectionReestablishmentRequest")
            #     # plt.scatter(self.iperffile.loc[k, "Time"], self.iperffile.loc[k, "Lost_p"], marker="^", c='r', label = "rrcConnectionReestablishmentRequest")
                
            #     if self.mifile.loc[i, "time"] - self.mifile.loc[j, "time"] > dt.timedelta(seconds=2):
            #         plt.axvline(self.mifile.loc[i, "time"], c = 'g', label = "nr-rrc.RRCReconfigurationComplete_element")

            #     # plt.axvline(self.mifile.loc[i, "time"], c = 'y', label = "nr-rrc.RRCReconfigurationComplete_element")



                        
            if self.mifile.loc[i, "scgFailureInformationNR-r15"]:
            #     j = i

            #     while self.iperffile.loc[k, "Time"] < self.mifile.loc[i, "time"]:
            #         k+=1


            #     while not ( self.mifile.loc[j, "nr-rrc.rrcReconfiguration_element"] == 1)  and j >=1:
            #         j -= 1
            #     print("type2: ", self.mifile.loc[j, "time"])
                plt.axvline(self.mifile.loc[i, "time"], c = c3, label = "scgFailureInformationNR-r15")
            #     # plt.scatter(self.iperffile.loc[k, "Time"], self.iperffile.loc[k, "Lost_p"], marker="^", c='black', label = "scgFailureInformationNR-r15")

            # if self.mifile.loc[i, "failureType-r15: randomAccessProblem (1)"]:
            #     while self.iperffile.loc[k, "Time"] < self.mifile.loc[i, "time"]:
            #         k+=1

            #     plt.scatter(self.iperffile.loc[k, "Time"], self.iperffile.loc[k, "Lost_p"], marker="^", c='black', label = "randomAccessProblem")

                # plt.axvline(self.mifile.loc[i, "time"], c = c4, label = "failureType-r15: randomAccessProblem (1)")


            # if self.mifile.loc[i, "rrcConnectionReestablishmentReject"]:

            #     while self.iperffile.loc[k, "Time"] < self.mifile.loc[i, "time"]:
            #         k+=1


                # print("r", self.mifile.loc[i, "time"])
                # plt.axvline(self.mifile.loc[i, "time"], c = 'k', label = "rrcConnectionReestablishmentReject")
                
                    # plt.scatter(self.iperffile.loc[k, "Time"], self.iperffile.loc[k, "Lost_p"], marker="^", c='g', label = "rrcConnectionReestablishmentReject")


            # if self.mifile.loc[i, "rrcConnectionReconfiguration"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = c3, label = "rrcConnectionReconfiguration")
            # if self.mifile.loc[i, "rrcConnectionReconfigurationComplete"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = c4, label = "rrcConnectionReconfigurationComplete")

            # if self.mifile.loc[i, "systemInformationBlockType5"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = '#ff7f0e', label = "systemInformationBlockType5")
            # if self.mifile.loc[i, "systemInformationBlockType6"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'xkcd', label = "systemInformationBlockType6")


            # if self.mifile.loc[i, "rrcConnectionSetup"]:
            #     plt.axvline(self.mifile.loc[i, "time"], c = 'pink', label = "rrcConnectionSetup")



        plt.xlim(self.begin_time, self.end_time)
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        plt.tight_layout()

        plt.subplot(414)
        plt.title("Jitter")
        ts = np.sort(self.iperffile.loc[:, "Jitter"])
        plt.ylim(ts[15], 2*ts[-45])
        plt.xlim(self.begin_time, self.end_time)

        plt.plot(self.iperffile.loc[:, "Time"], self.iperffile.loc[:, "Jitter"])
        j = 0
        # for i in range(len(self.mifile)):
            
        #     if self.mifile.loc[i, r"nr-rrc.RRCReconfigurationComplete_element"]:
        #         j = i
        #         # while self.iperffile.loc[k, "Time"] < self.mifile.loc[i, "time"]:
        #         #     k+=1
        #         while not (self.mifile.loc[j, "t304"] == 1):
        #             j -= 1
        #         if self.mifile.loc[i, "time"] - self.mifile.loc[j, "time"] > dt.timedelta(seconds=2):
        #             # print("handoff time:", self.mifile.loc[i, "time"] - self.mifile.loc[j, "time"], self.mifile.loc[i, "time"], self.mifile.loc[j, "time"])
        #             plt.axvline(self.mifile.loc[i, "time"], c = 'g', label = "nr-rrc.RRCReconfigurationComplete_element")
                
        #         # plt.scatter(self.iperffile.loc[i, "Time"], self.iperffile.loc[k, "Lost_p"], marker="^", c='r', label = "rrcConnectionReestablishmentRequest")


        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.show()



        print(self.mifile.loc[:, "rrcConnectionReconfigurationComplete"].sum(), self.mifile.loc[:, "rrcConnectionReconfiguration"].sum())


if __name__ == "__main__":
    X = Signal(mifile="diag_log_20210830_185225.txt.csv", iperffile="DL_0830.txt.csv", cellinfofile = "083021063811.csv2.csv")
    X.show_figure()