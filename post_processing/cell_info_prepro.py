import pandas as pd


fname = "083021063811.csv"
names = ["Date",
"RxRate",
"TxRate",
"DLBandwidth",
"ULBandwidth",
"LTE",
"LTE_RSRP",
"LTE_RSRQ",
"NR",
"NR_SSRSRP",
"NR_SSRSRQ",
"NR_CSIRSRP",
"NR_CSIRSRQ",
"Type",
"MNC",
"MCC",
"CID",
"PCI",
"SigStrength",
"earfcn"]

df = pd.read_csv(fname, names=names)

def to_zero(x):
    return x if x != '-' else 0


df.loc[:, "NR_SSRSRP"] = df.loc[:, "NR_SSRSRP"].apply(to_zero)
df.loc[:, "NR_SSRSRQ"] = df.loc[:, "NR_SSRSRQ"].apply(to_zero)
df.loc[:, "NR_CSIRSRP"] = df.loc[:, "NR_CSIRSRP"].apply(to_zero)
df.loc[:, "NR_CSIRSRQ"] = df.loc[:, "NR_CSIRSRQ"].apply(to_zero)

df.to_csv(fname+"2.csv", index=False)
# df.to_csv()

print(df)

