import pandas as pd

fname = r"C:\Users\User\Desktop\UEdata\1\cellinfo0.csv"
def prepro(fname):

    names = ["Date","GPSLat","GPSLon","GPSSpeed","RxRate","TxRate","DLBandwidth","ULBandwidth","MNC","MCC","CID","PCI","LTE_RSRP","LTE_RSRQ","NR_SSRSRP","NR_SSRSRQ","earfcn","PCI1","LTE_RSRP1","LTE_RSRQ1","earfcn1","PCI2","LTE_RSRP2","LTE_RSRQ2","earfcn2","PCI3","LTE_RSRP3","LTE_RSRQ3","earfcn3","PCI4","LTE_RSRP4","LTE_RSRQ4","earfcn4","PCI5","LTE_RSRP5","LTE_RSRQ5","earfcn5","PCI6","LTE_RSRP6","LTE_RSRQ6","earfcn6","PCI7","LTE_RSRP7","LTE_RSRQ7","earfcn7","PCI8","LTE_RSRP8","LTE_RSRQ8","earfcn8","PCI9","LTE_RSRP9","LTE_RSRQ9","earfcn9","PCI10","LTE_RSRP10","LTE_RSRQ10",]
    f = open(fname, "r")
    strlist = f.readlines()
    f.close()
    if strlist[0][:4] == "Date":
        strlist[0] = ",".join(names)
        f = open(fname, "w")
        f.write("".join(strlist))
    else:
        strlist = ",".join(names) + strlist
        f = open(fname, "w")
        f.write("".join(strlist))


if __name__ == "__main__":
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

