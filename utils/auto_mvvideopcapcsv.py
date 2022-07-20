from genericpath import exists
import sys
import os
import shutil
import pandas as pd


pcap_csv_dir = r"/home/wmnlab/D/video_streamming"
pcap_csv_dir2 = r"/home/wmnlab/D/laptop1"
D_dir = r"/home/wmnlab/D/"

device = "video_streamming"


def savemove(targetdir, filepath, filename):
    if not os.path.exists(targetdir):
        os.mkdir(targetdir)
    print("mv", filepath, os.path.join(targetdir, filename))
    shutil.move(filepath, os.path.join(targetdir, filename))

def get_pcap_date(pcapfile):
    try:
        df = pd.read_csv(pcapfile, sep="@", encoding="ISO-8859-1")
        d = pd.to_datetime(df.loc[0, 'frame.time'])
        d = ("%2d%2d"%(d.month, d.day)).replace(" ", "0")
    except Exception as e:
        print(e)
        return "-1"
    return d

def is_server_pcap_csv(filename):
    return "server" in filename and "pcap" in filename and ".csv" in filename

def is_client_pcap_csv(filename):
    return "client" in filename and "pcap" in filename and ".csv" in filename


for filename in os.listdir(pcap_csv_dir):
    filepath = os.path.join(pcap_csv_dir, filename)


    if is_server_pcap_csv(filename):

        if device == "-1":
            continue
        date = get_pcap_date(filepath)

        if date == "-1":
            print("rm", filepath, "?")
            # os.remove(filepath)
            continue
        print(filename, device, date)

        targetdir = os.path.join(D_dir, device, date, "server_pcapcsv")

        if not os.path.exists(os.path.join(D_dir, device)):
            os.mkdir(os.path.join(os.path.join(D_dir, device)))

        if not os.path.exists(os.path.join(D_dir, device, date)):
            os.mkdir(os.path.join(os.path.join(D_dir, device, date)))

        if not os.path.exists(targetdir):
            os.mkdir(targetdir)

        savemove(targetdir, filepath, filename)


for filename in os.listdir(pcap_csv_dir2):
    # print(filename)
    filepath = os.path.join(pcap_csv_dir2, filename)


    if is_client_pcap_csv(filename):

        if device == "-1":
            continue
        date = get_pcap_date(filepath)

        if date == "-1":
            print("rm", filepath, "?")
            # os.remove(filepath)
            continue
        print(filename, device, date)

        targetdir = os.path.join(D_dir, device, date, "client_pcapcsv")

        if not os.path.exists(os.path.join(D_dir, device)):
            os.mkdir(os.path.join(os.path.join(D_dir, device)))

        if not os.path.exists(os.path.join(D_dir, device, date)):
            os.mkdir(os.path.join(os.path.join(D_dir, device, date)))

        if not os.path.exists(targetdir):
            os.mkdir(targetdir)

        savemove(targetdir, filepath, filename)
    