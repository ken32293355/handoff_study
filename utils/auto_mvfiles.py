from genericpath import exists
import sys
import os
import shutil
import pandas as pd

dirpath = sys.argv[1]

def is_pcap_csv(filename):
    return "pcap" in filename and ".csv" in filename
def is_cellinfo_csv(filename):
    return not "pcap" in filename and not ("-") in filename and ".csv" in filename and "_new" in filename
def is_mi2log_csv(filename):
    return "mi2log" in filename and "csv" in filename

def savemove(targetdir, filepath, filename):
    if not os.path.exists(targetdir):
        os.mkdir(targetdir)
    print("mv", filepath, os.path.join(targetdir, filename))
    shutil.move(filepath, os.path.join(targetdir, filename))

def get_pcap_date(pcapfile):
    try:
        df = pd.read_csv(pcapfile, sep="@")
        d = pd.to_datetime(df.loc[0, 'frame.time'])
        d = ("%2d%2d"%(d.month, d.day)).replace(" ", "0")
    except:
        return "-1"
    return d

def get_cellinfo_date(cellinfofile):
    print(cellinfofile)

    df = pd.read_csv(cellinfofile)
    try:
        d = pd.to_datetime(df.loc[0, 'Date'])
        d = ("%2d%2d"%(d.month, d.day)).replace(" ", "0")
    except:
        return "-1"
    return d

def get_mi2log_date(cellinfofile):
    try:
        df = pd.read_csv(cellinfofile)
        d = pd.to_datetime(df.loc[0, 'time'])
        d = ("%2d%2d"%(d.month, d.day)).replace(" ", "0")
    except:
        return "-1"
    return d





for filename in os.listdir(dirpath):
    filepath = os.path.join(dirpath, filename)
    if is_pcap_csv(filepath):
        date = get_pcap_date(filepath)
        if not os.path.exists( os.path.join(dirpath, date) ):
            os.mkdir(os.path.join(dirpath, date))
        savemove(os.path.join(dirpath, date, "pcap"), filepath, filename)
    if is_cellinfo_csv(filepath):
        date = get_cellinfo_date(filepath)
        if not os.path.exists( os.path.join(dirpath, date) ):
            os.mkdir(os.path.join(dirpath, date))
        savemove(os.path.join(dirpath, date, "cellinfo"), filepath, filename)
    if is_mi2log_csv(filepath):
        date = get_mi2log_date(filepath)
        if not os.path.exists( os.path.join(dirpath, date) ):
            os.mkdir(os.path.join(dirpath, date))
        savemove(os.path.join(dirpath, date, "mi2log"), filepath, filename)
    
