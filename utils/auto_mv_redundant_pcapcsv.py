from genericpath import exists
import sys
import os
import shutil
import pandas as pd


pcap_csv_dir = sys.argv[1]
D_dir = r"/home/wmnlab/D/"

band_to_device ={
    "3231": "xm00", #886
    "3232": "xm00",
    "3233": "xm01",
    "3234": "xm01",
    "3235": "xm02",
    "3236": "xm02",
    "3237": "xm03",
    "3238": "xm03",
    "3239": "xm04",
    "3240": "xm04",
    "3241": "xm05",
    "3242": "xm05",
    "3265": "xm06",
    "3266": "xm06",
    "3243": "xm07",
    "3244": "xm07",
    "3245": "xm08",
    "3246": "xm08",
    "3247": "xm09",
    "3248": "xm09",
    "3249": "xm10",
    "3250": "xm10",
    "3251": "xm11",
    "3252": "xm11",
    "3253": "xm12",
    "3254": "xm12",
    "3255": "xm13",
    "3256": "xm13",
    "3257": "xm14",
    "3258": "xm14",
    "3259": "xm15",
    "3260": "xm15",
    "3261": "xm16",
    "3262": "xm16",
    "3263": "xm17",
    "3264": "xm17",
    "3271": "mptcpsocket",
}

def get_begin_time(filename):
    try:
        return filename[15:filename.find("_pcap")]
    except:
        return "-1"
def get_device(filename):
    port = filename[10:14]
    if port.isdigit():
        if int(port) >= 3070:
            return "redundant"
    for band in band_to_device:
        if band in filename:
            return band_to_device[band]
    return "-1"

def is_server_ul_pcap_csv(filename):
    return "server" in filename and "UL" in filename and "pcap" in filename and ".csv" in filename

def is_server_dl_pcap_csv(filename):
    return "server" in filename and "DL" in filename and "pcap" in filename and ".csv" in filename


def is_client_ul_pcap_csv(filename):
    return "client" in filename and "UL" in filename and "pcap" in filename and ".csv" in filename

def is_client_dl_pcap_csv(filename):
    return "client" in filename and "DL" in filename and "pcap" in filename and ".csv" in filename

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

for filename in os.listdir(pcap_csv_dir):
    filepath = os.path.join(pcap_csv_dir, filename)


    filetype = "-1"

    if is_server_ul_pcap_csv(filepath):
        filetype = "server_ul_pcap"
    elif is_server_dl_pcap_csv(filepath):
        filetype = "server_dl_pcap"
        device = get_device(filename)
    elif is_client_ul_pcap_csv(filepath):
        filetype = "client_ul_pcap"
    elif is_client_dl_pcap_csv(filepath):
        filetype = "client_dl_pcap"

    device = "redundant"


    date = get_pcap_date(filepath)

    if date == "-1":
        # os.remove(filepath)
        continue

    begin_time = get_begin_time(filename)
    if begin_time == "-1":
        # os.remove(filepath)
        continue
    
    if filetype == "-1":
        continue
    

    print(filename, device, date, begin_time)

    targetdir = os.path.join(D_dir, device, date, filetype, begin_time)

    if not os.path.exists(os.path.join(D_dir, device)):
        os.mkdir(os.path.join(os.path.join(D_dir, device)))

    if not os.path.exists(os.path.join(D_dir, device, date)):
        os.mkdir(os.path.join(os.path.join(D_dir, device, date)))

    if not os.path.exists(os.path.join(D_dir, device, date, filetype)):
        os.mkdir(os.path.join(os.path.join(D_dir, device, date, filetype)))

    if not os.path.exists(targetdir):
        os.mkdir(targetdir)

    savemove(targetdir, filepath, filename)

