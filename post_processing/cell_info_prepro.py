import pandas as pd

fname = r"C:\Users\User\Desktop\UEdata\1\cellinfo0.csv"
def prepro(fname):

    names = ["Date","GPSLat","GPSLon","GPSSpeed","RxRate","TxRate","DLBandwidth","ULBandwidth","MNC","MCC","CID","PCI","LTE_RSRP","LTE_RSRQ","NR_SSRSRP","NR_SSRSRQ","earfcn","PCI1","LTE_RSRP1","LTE_RSRQ1","earfcn1","PCI2","LTE_RSRP2","LTE_RSRQ2","earfcn2","PCI3","LTE_RSRP3","LTE_RSRQ3","earfcn3","PCI4","LTE_RSRP4","LTE_RSRQ4","earfcn4","PCI5","LTE_RSRP5","LTE_RSRQ5","earfcn5","PCI6","LTE_RSRP6","LTE_RSRQ6","earfcn6","PCI7","LTE_RSRP7","LTE_RSRQ7","earfcn7","PCI8","LTE_RSRP8","LTE_RSRQ8","earfcn8","PCI9","LTE_RSRP9","LTE_RSRQ9","earfcn9","PCI10","LTE_RSRP10","LTE_RSRQ10","earfcn10","PCI11","LTE_RSRP11","LTE_RSRQ11","earfcn11","PCI12","LTE_RSRP12","LTE_RSRQ12","earfcn12","PCI13","LTE_RSRP13","LTE_RSRQ13","earfcn13","PCI14","LTE_RSRP14","LTE_RSRQ14","earfcn14","PCI15","LTE_RSRP15","LTE_RSRQ15","earfcn15","PCI16","LTE_RSRP16","LTE_RSRQ16","earfcn16","PCI17","LTE_RSRP17","LTE_RSRQ17","earfcn17","PCI18","LTE_RSRP18","LTE_RSRQ18","earfcn18","PCI19","LTE_RSRP19","LTE_RSRQ19","earfcn19","PCI20","LTE_RSRP20","LTE_RSRQ20","earfcn20","PCI21","LTE_RSRP21","LTE_RSRQ21","earfcn21", ]
    f = open(fname, "r")
    strlist = f.readlines()
    f.close()
    if strlist[0][:4] == "Date":
        strlist[0] = ",".join(names) + '\n'
        f = open(fname, "w")
        f.write("".join(strlist))
    else:
        strlist = (",".join(names) + '\n') + strlist
        f = open(fname, "w")
        f.write("".join(strlist))


if __name__ == "__main__":
    # fname = r"C:\Users\User\Desktop\data\0117\samsung_\round1.csv"
    # prepro(fname)
    # fname = r"C:\Users\User\Desktop\data\0117\samsung_\round2.csv"
    # prepro(fname)
    # fname = r"C:\Users\User\Desktop\data\0117\\xiaomi\846-908.csv"
    # prepro(fname)
    # fname = r"C:\Users\User\Desktop\data\0117\\xiaomi\905-935.csv"
    # prepro(fname)
    # fname = r"C:\Users\User\Desktop\data\0117\\xiaomi\924-35.csv"
    # prepro(fname)
    fname = r"C:\Users\User\Desktop\data\0117\s20\round1.csv"
    prepro(fname)
    fname = r"C:\Users\User\Desktop\data\0117\s20\round2.csv"
    prepro(fname)

# df = pd.read_csv(fname, names=names)
# print(df)
# def to_zero(x):
#     return x if x != '-' else 0
# # df.loc[:, "NR_SSRSRP"] = df.loc[:, "NR_SSRSRP"].apply(to_zero)
# # df.loc[:, "NR_SSRSRQ"] = df.loc[:, "NR_SSRSRQ"].apply(to_zero)
# # df.loc[:, "NR_CSIRSRP"] = df.loc[:, "NR_CSIRSRP"].apply(to_zero)
# # df.loc[:, "NR_CSIRSRQ"] = df.loc[:, "NR_CSIRSRQ"].apply(to_zero)
# # df.to_csv(fname+"2.csv", index=False)
# # # df.to_csv()
# # print(df)

