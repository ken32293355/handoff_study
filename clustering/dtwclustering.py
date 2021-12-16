# Author: Romain Tavenard
# License: BSD 3 clause

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import os
from tslearn.clustering import TimeSeriesKMeans
from tslearn.datasets import CachedDatasets
from tslearn.preprocessing import TimeSeriesScalerMeanVariance, \
    TimeSeriesResampler


mifile = "diag_log_20211003_211709_3c882bf9be1231f3a50006ebef5e380e_Xiaomi-M2007J3SY_46697.mi2log.txt.csv"
cellinfo = "100321090205.csv2.csvver2.csv"
cellinfo = "100321090205.csv"
step = 5

mifilenanme_l = ["diag_log_20211003_211709_3c882bf9be1231f3a50006ebef5e380e_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_220536_3c882bf9be1231f3a50006ebef5e380e_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_223825_3c882bf9be1231f3a50006ebef5e380e_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_230802_3c882bf9be1231f3a50006ebef5e380e_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_234301_3c882bf9be1231f3a50006ebef5e380e_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_220533_aaa4dc12971e6450aedde3a6ea3adb20_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_222217_aaa4dc12971e6450aedde3a6ea3adb20_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_222217_aaa4dc12971e6450aedde3a6ea3adb20_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
"diag_log_20211010_230807_aaa4dc12971e6450aedde3a6ea3adb20_Xiaomi-M2007J3SY_46697.mi2log.txt.csv",
]
cellinfo_l = ["100321090205.csv", "101021095655.csv",
"101021102800.csv", "101021110043.csv", "101021113118.csv",
"101021095654.csv",
"101021101412.csv",
"101021102808.csv",
"101021105648.csv"
]


def read_file(mifile, cellinfo, STEP):
    print(mifile)
    mifile_df = pd.read_csv(mifile)

    mifile_df.loc[:, "time"] = pd.to_datetime(mifile_df.loc[:, "time"]) + dt.timedelta(hours=8)


    mifile_df.set_index("time", inplace=True)
    mifile_df = mifile_df.resample('1s').sum()

    mifile_df.reset_index(inplace = True)

    cellinfo_df = pd.read_csv(cellinfo)

    cellinfo_df.loc[:, "Date"] = pd.to_datetime(cellinfo_df.loc[:, "Date"])
    cellinfo_df.set_index("Date", inplace=True)
    
    cellinfo_df = cellinfo_df[~cellinfo_df.index.duplicated(keep='first')]

    cellinfo_df = cellinfo_df.resample('1s').pad()
    cellinfo_df.reset_index(inplace = True)


    def to_zero(x):
        return x if x != '-' else 0
    def to_zero_(x):
        if type(x) == type(" "):
            return 0
        return 0 if np.isnan(x) else x

    cellinfo_df.loc[:, "SigStrength1"] = cellinfo_df.loc[:, "SigStrength1"].apply(to_zero_)
    cellinfo_df.loc[:, "NR_SSRSRP"] = cellinfo_df.loc[:, "NR_SSRSRP"].apply(to_zero)
    cellinfo_df.loc[:, "NR_SSRSRQ"] = cellinfo_df.loc[:, "NR_SSRSRQ"].apply(to_zero)
    cellinfo_df.loc[:, "NR_CSIRSRP"] = cellinfo_df.loc[:, "NR_CSIRSRP"].apply(to_zero)
    cellinfo_df.loc[:, "NR_CSIRSRQ"] = cellinfo_df.loc[:, "NR_CSIRSRQ"].apply(to_zero)

    begin_time = max(mifile_df.loc[0, "time"], cellinfo_df.loc[0, "Date"])
    begin_time = begin_time.replace(microsecond = 0) + dt.timedelta(seconds=1)


    end_time = min(mifile_df.loc[mifile_df.index[-1], "time"], cellinfo_df.loc[cellinfo_df.index[-1], "Date"])
    end_time = end_time.replace(microsecond = 0) - dt.timedelta(seconds=1)


    mifile_df = mifile_df[(mifile_df.loc[:, "time"]> begin_time) & (mifile_df.loc[:, "time"]< end_time)]
    mifile_df.reset_index(inplace = True)


    cellinfo_df = cellinfo_df[(cellinfo_df.loc[:, "Date"]> begin_time) & (cellinfo_df.loc[:, "Date"]< end_time)]
    cellinfo_df.reset_index(inplace = True)

    if len(mifile_df) ==0 or len(cellinfo_df) ==0:
        print("empty list")
        return [], [], [], []

    STEP = 5

    lte_rsrp_l = []
    nr_rsrp_l = []
    sigstrength1_l = []
    mifile_l = []
    for i in range(0, len(cellinfo_df)-STEP):
        lte_rsrp_l.append(cellinfo_df.loc[i:i+STEP, "LTE_RSRP"])
        nr_rsrp_l.append(cellinfo_df.loc[i:i+STEP, "NR_SSRSRP"])
        sigstrength1_l.append(cellinfo_df.loc[i:i+STEP, "SigStrength1"])
        mifile_l.append(mifile_df.loc[i+STEP:i+STEP+2])



    return lte_rsrp_l, nr_rsrp_l, sigstrength1_l, mifile_l


sigstrength1_l = []
lte_rsrp_l = []
nr_rsrp_l = []
mifile_l = []

assert(len(mifilenanme_l) == len(cellinfo_l))

for mifile, cellinfo in zip(mifilenanme_l, cellinfo_l):
    lte_rsrp_l_, nr_rsrp_l_, sigstrength1_l_, mifile_l_ = read_file(os.path.join("mifile", mifile), os.path.join("cellinfo", cellinfo), STEP = 5)
    lte_rsrp_l += lte_rsrp_l_
    nr_rsrp_l += nr_rsrp_l_
    sigstrength1_l += sigstrength1_l_
    mifile_l += mifile_l_

sigstrength1_l = np.array(sigstrength1_l)
lte_rsrp_l = np.array(lte_rsrp_l)
nr_rsrp_l = np.array(nr_rsrp_l)
sigstrength1_l[np.isnan(sigstrength1_l)] = 0

seed = 123

# Euclidean k-means


lte_num_cluster = 20
km_lte = TimeSeriesKMeans(n_clusters=lte_num_cluster, verbose=True, random_state=seed)
lte_rsrp_l_y_pred = km_lte.fit_predict(lte_rsrp_l)

# km_nr = TimeSeriesKMeans(n_clusters=20, verbose=True, random_state=seed, metric = "dtw", n_jobs = -1, max_iter_barycenter=50,)

# km_nr = TimeSeriesKMeans(n_clusters=20, verbose=True, random_state=seed, n_jobs = -1, max_iter_barycenter=50,)
# nr_rsrp_l_y_pred = km_nr.fit_predict(nr_rsrp_l)

km_sigstrength1 = TimeSeriesKMeans(n_clusters=20, metric="softdtw", max_iter=5,
                            max_iter_barycenter=5,
                            metric_params={"gamma": .5},
                            random_state=0)

km_sigstrength1 = TimeSeriesKMeans(n_clusters=20, verbose=True, random_state=seed, n_jobs = -1, max_iter_barycenter=50,)



sigstrength1_l_y_pred = km_sigstrength1.fit_predict(sigstrength1_l)

handoff_count = np.zeros([lte_num_cluster, 20], dtype="int")
type_total = np.zeros([lte_num_cluster, 20], dtype="int")

# packet_loss_count = {}
# packet_loss_total = {}


print(sigstrength1_l_y_pred)


for i in range(len(mifile_l)):
    type_total[lte_rsrp_l_y_pred[i], sigstrength1_l_y_pred[i]] += 1
    if mifile_l[i].loc[:, "lte-rrc.t304"].any():
        handoff_count[lte_rsrp_l_y_pred[i], sigstrength1_l_y_pred[i]] += 1


print(type_total)
print(handoff_count)
ratio = (handoff_count/type_total * 100).astype("int")
ratio[np.isnan(ratio)] = 0
ratio[ratio<0] = 0
print(ratio)

print(np.sum((ratio > 70 ) & (type_total > 5) ))
print(np.where((ratio > 70 ) & (type_total > 5) ))


for i in range(lte_num_cluster):
    for j in range(20):
        if ratio[i, j] > 70 and type_total[i, j] > 5:
            plt.subplot(2, 1, 1)
            plt.plot(km_lte.cluster_centers_[i].ravel(), "r-")
            plt.subplot(2, 1, 2)
            plt.plot(km_sigstrength1.cluster_centers_[j].ravel(), "r-")
            plt.show()


plt.figure()

# for yi in range(20):
#     plt.whereplot(3, 20, yi + 1)
#     for xx in nr_rsrp_l[nr_rsrp_l_y_pred == yi]:
#         plt.plot(xx.ravel(), "k-", alpha=.2)
#     plt.plot(km_nr.cluster_centers_[yi].ravel(), "r-")
#     # plt.xlim(0, STEP)
#     # plt.ylim(-4, 4)
#     plt.text(0.55, 0.85,'Cluster %d' % (yi + 1),
#              transform=plt.gca().transAxes)
#     if yi == 1:
#         plt.title("nr $k$-means")


for yi in range(lte_num_cluster):
    # plt.suptitle("lte rsrp clustering")

    plt.subplot(2, 20, yi + 1)
    # plt.title('C %d' % (yi))
    for xx in lte_rsrp_l[lte_rsrp_l_y_pred == yi]:
        plt.plot(xx.ravel(), "k-", alpha=.2)
    plt.plot(km_lte.cluster_centers_[yi].ravel(), "r-")
    # plt.xlim(0, STEP)
    # plt.ylim(-4, 4)
    plt.text(0.25, 0.85,'C%d' % (yi + 1),
             transform=plt.gca().transAxes)
    if yi == 1:
        plt.title("lte $k$-means")

for yi in range(20):
    plt.subplot(2, 20, lte_num_cluster + yi + 1)
    # plt.title('C %d' % (yi))
    # plt.title("sigstrength1 $k$-means")

    for xx in sigstrength1_l[sigstrength1_l_y_pred == yi]:
        plt.plot(xx.ravel(), "k-", alpha=.2)
    plt.plot(km_sigstrength1.cluster_centers_[yi].ravel(), "r-")
    # plt.xlim(0, STEP)
    # plt.ylim(-4, 4)
    plt.text(0.25, 0.85,'C %d' % (yi + 1),
             transform=plt.gca().transAxes)
    if yi == 1:
        plt.title("sigstrength1 $k$-means")
    plt.tight_layout()


# # DBA-k-means
# print("DBA k-means")
# dba_km = TimeSeriesKMeans(n_clusters=3,
#                           n_init=2,
#                           metric="dtw",
#                           verbose=True,
#                           max_iter_barycenter=10,
#                           random_state=seed)
# y_pred = dba_km.fit_predict(X_train)

# for yi in range(3):
#     plt.subplot(3, 3, 4 + yi)
#     for xx in X_train[y_pred == yi]:
#         plt.plot(xx.ravel(), "k-", alpha=.2)
#     plt.plot(dba_km.cluster_centers_[yi].ravel(), "r-")
#     plt.xlim(0, sz)
#     plt.ylim(-4, 4)
#     plt.text(0.55, 0.85,'Cluster %d' % (yi + 1),
#              transform=plt.gca().transAxes)
#     if yi == 1:
#         plt.title("DBA $k$-means")

# # Soft-DTW-k-means
# print("Soft-DTW k-means")
# sdtw_km = TimeSeriesKMeans(n_clusters=3,
#                            metric="softdtw",
#                            metric_params={"gamma": .01},
#                            verbose=True,
#                            random_state=seed)
# y_pred = sdtw_km.fit_predict(X_train)

# for yi in range(3):
#     plt.subplot(3, 3, 7 + yi)
#     for xx in X_train[y_pred == yi]:
#         plt.plot(xx.ravel(), "k-", alpha=.2)
#     plt.plot(sdtw_km.cluster_centers_[yi].ravel(), "r-")
#     plt.xlim(0, sz)
#     plt.ylim(-4, 4)
#     plt.text(0.55, 0.85,'Cluster %d' % (yi + 1),
#              transform=plt.gca().transAxes)
#     if yi == 1:
#         plt.title("Soft-DTW $k$-means")

# plt.tight_layout()
plt.show()




