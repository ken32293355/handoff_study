import readline
import numpy as np
import pandas as pd
import os
import datetime as dt
def pci_changetime(df):
    time_l = []
    prev_pci = df.loc[0, "PCI"]
    for i in range(1, len(df)):
        if prev_pci != df.loc[i, 'PCI']:
            time_l.append(df.loc[i, 'Date'])
        prev_pci = df.loc[i, 'PCI']
    return np.array(time_l)
def compare(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df1.loc[:, "Date"] = pd.to_datetime(df1.loc[:, "Date"])
    df2.loc[:, "Date"] = pd.to_datetime(df2.loc[:, "Date"])
    begintime = max(df1.loc[0, "Date"], df2.loc[0, "Date"])
    endtime = min(df1.loc[df1.index[-1], "Date"], df2.loc[df2.index[-1], "Date"])
    df1 = df1[(df1.loc[:, "Date"]>=begintime) & (df1.loc[:, "Date"]<=endtime)]
    df2 = df2[(df2.loc[:, "Date"]>=begintime) & (df2.loc[:, "Date"]<=endtime)]
    df1.reset_index(inplace=True)
    df2.reset_index(inplace=True)
    time_l1 = pci_changetime(df1)
    time_l2 = pci_changetime(df2)
    print(set(df1.loc[:, "earfcn"]))
    print(set(df2.loc[:, "earfcn"]))
    diff_l1 = np.empty_like(time_l1)
    diff_l2 = np.empty_like(time_l2)
    for i in range(len(time_l1)):
        diff_l1[i] = np.abs(time_l1[i]-time_l2).min()
    for i in range(len(time_l2)):
        diff_l2[i] = np.abs(time_l2[i]-time_l1).min()


    # print(diff_l1)
    # print(diff_l2)
    onesecond = dt.timedelta(seconds=1)
    twosecond = dt.timedelta(seconds=2)
    print(len(diff_l1), (diff_l1 > onesecond).sum() / len(diff_l1), (diff_l1 <= onesecond).sum() / len(diff_l1))
    print(len(diff_l2), (diff_l2 > onesecond).sum() / len(diff_l2), (diff_l2 <= onesecond).sum() / len(diff_l2))

    print(len(diff_l1), (diff_l1 > twosecond).sum() / len(diff_l1), (diff_l1 <= twosecond).sum() / len(diff_l1))
    print(len(diff_l2), (diff_l2 > twosecond).sum() / len(diff_l2), (diff_l2 <= twosecond).sum() / len(diff_l2))
    exit()

    return diff_l1, diff_l2

if __name__ == "__main__":
    """
        cellinfo1: 9560
        9560 1275

    {9560}
    {9560.0, 1275.0}
    13 0.46153846153846156 0.5384615384615384
    17 0.5294117647058824 0.47058823529411764
    13 0.15384615384615385 0.8461538461538461
    17 0.17647058823529413 0.8235294117647058


    """
    # datasetpath = r"C:\Users\User\Desktop\UEdata"
    # file1 = os.path.join(datasetpath, "0", "cellinfo0.csv")
    # file2 = os.path.join(datasetpath, "1", "cellinfo0.csv")
    # compare(file1=file1, file2=file2)

    """
    {9560, 275, 1275}
    {275, 9560, 1275}
    47 0.9574468085106383 0.0425531914893617
    30 0.9333333333333333 0.06666666666666667
    47 0.851063829787234 0.14893617021276595
    30 0.7666666666666667 0.23333333333333334
    """

    # datasetpath = r"C:\Users\User\Desktop\UEdata"
    # file1 = os.path.join(datasetpath, "0", "cellinfo1.csv")
    # file2 = os.path.join(datasetpath, "1", "cellinfo1.csv")
    # compare(file1=file1, file2=file2)
    """
    {9560, 275, 1275}
    {9560, 275, 1275}
    83 0.9397590361445783 0.060240963855421686
    40 0.875 0.125
    83 0.891566265060241 0.10843373493975904
    40 0.775 0.225
    """

    # datasetpath = r"C:\Users\User\Desktop\UEdata"
    # file1 = os.path.join(datasetpath, "0", "cellinfo2.csv")
    # file2 = os.path.join(datasetpath, "1", "cellinfo2.csv")
    # compare(file1=file1, file2=file2)


    """
    {9560, 9610, 275, 1275}
    {nan, nan, 9610.0, 275.0, 9560.0, 1275.0}
    178 0.9213483146067416 0.07865168539325842
    117 0.8717948717948718 0.1282051282051282
    178 0.8426966292134831 0.15730337078651685
    117 0.7521367521367521 0.24786324786324787
    """

    # datasetpath = r"C:\Users\User\Desktop\UEdata"
    # file1 = os.path.join(datasetpath, "0", "cellinfo3.csv")
    # file2 = os.path.join(datasetpath, "1", "cellinfo3.csv")
    # compare(file1=file1, file2=file2)

    """
    {9560, 275}
    {9560, 275}
    32 0.71875 0.28125
    25 0.64 0.36
    32 0.65625 0.34375
    25 0.56 0.44
    """

    # datasetpath = r"C:\Users\User\Desktop\data\0117"
    # file1 = os.path.join(datasetpath, "samsung", "round1.csv")
    # file2 = os.path.join(datasetpath, "xiaomi", "round1.csv")
    # compare(file1=file1, file2=file2)

    """
    {9560, 9610}
    {1275}
    80 0.825 0.175
    76 0.8157894736842105 0.18421052631578946
    80 0.6625 0.3375
    76 0.631578947368421 0.3684210526315789
    """

    # datasetpath = r"C:\Users\User\Desktop\data\0117"
    # file1 = os.path.join(datasetpath, "samsung", "round2.csv")
    # file2 = os.path.join(datasetpath, "xiaomi", "round2.csv")
    # compare(file1=file1, file2=file2)

    """
    TW mobile vs cht

    {9560, 275}
    {1400, 3050, 1750}
    85 0.9882352941176471 0.011764705882352941
    30 0.9666666666666667 0.03333333333333333
    85 0.9647058823529412 0.03529411764705882
    30 0.9 0.1

    """

    # datasetpath = r"C:\Users\User\Desktop\data\0117"
    # file1 = os.path.join(datasetpath, "samsung", "round1.csv")
    # file2 = os.path.join(datasetpath, "s20", "round1.csv")
    # compare(file1=file1, file2=file2)

    """
    {9560, 9610}
    {1400, 3050}
    88 0.9204545454545454 0.07954545454545454
    32 0.75 0.25
    88 0.8863636363636364 0.11363636363636363
    32 0.6875 0.3125
    """

    # datasetpath = r"C:\Users\User\Desktop\data\0117"
    # file1 = os.path.join(datasetpath, "samsung", "round2.csv")
    # file2 = os.path.join(datasetpath, "s20", "round2.csv")
    # compare(file1=file1, file2=file2)
    """
    {275}
    {1400, 1750}
    22 0.9545454545454546 0.045454545454545456
    8 0.875 0.125
    22 0.9545454545454546 0.045454545454545456
    8 0.875 0.125
    """

    datasetpath = r"C:\Users\User\Desktop\data\0117"
    file1 = os.path.join(datasetpath, "xiaomi", "round1.csv")
    file2 = os.path.join(datasetpath, "s20", "round1.csv")
    # compare(file1=file1, file2=file2)
    """
    {1275}
    {1400, 3050}
    73 0.9726027397260274 0.0273972602739726
    28 0.9285714285714286 0.07142857142857142
    73 0.9315068493150684 0.0684931506849315
    28 0.7857142857142857 0.21428571428571427
    """

    datasetpath = r"C:\Users\User\Desktop\data\0117"
    file1 = os.path.join(datasetpath, "xiaomi", "round2.csv")
    file2 = os.path.join(datasetpath, "s20", "round2.csv")
    compare(file1=file1, file2=file2)


