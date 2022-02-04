######xml_mi.py#########
#==============instructions==============
######This file requires the txt file which is generated from offline_analysis.py and the mi2log file
######The rows shows the information of each diag mode packets (dm_log_packet) from Mobile Insight 
######The columns are indicators about whether a packet has the type of the message

from bs4 import BeautifulSoup
import sys
import os

dirname = sys.argv[1]

filenames = os.listdir(dirname)

for fname in filenames:
    if fname[-4:] != '.txt':
        continue
        
    print(fname)
    f = open(sys.argv[1] + fname, encoding="utf-8")
    f2 = open(sys.argv[1] + fname+'_3.csv', 'w')
    print(">>>>>")
    #Writing the column names...
    #-------------------------------------------------
    f2.write(",".join(["time", "type_id",
        "PCI",
        "UL_DL",
        "measurementReport",
        "rrcConnectionReconfiguration",
        "rrcConnectionReestablishmentRequest",
        "rrcConnectionReestablishment",
        "rrcConnectionReestablishmentReject",
        "rrcConnectionSetup",
        "rrcConnectionSetupComplete",
        "lte-rrc.nr_SecondaryCellGroupConfig_r15",
        "rrcConnectionReconfigurationComplete",   
        "scgFailureInformationNR-r15",
        "nr-rrc.t304",
        "lte-rrc.t304",
        "nr-Config-r15: release (0)",
        "nr-Config-r15: setup (1)",
        "dualConnectivityPHR: setup (1)",
        "dualConnectivityPHR: release (0)",
        "nr-rrc.RRCReconfiguration_element",
        "nr-rrc.eventA",
        "nr-rrc.spCellConfig_element",
        "lte-rrc.targetPhysCellId",
        "nr_pci"])+'\n')

    l = f.readline()

    #For each dm_log_packet, we will check that whether strings in type_list are shown in it.
    #If yes, type_code will record what types in type_list are shown in the packet.
    #-------------------------------------------------
    type_list = [
        "\"measurementReport\"",
        "\"rrcConnectionReconfiguration\"",
        "\"rrcConnectionReestablishmentRequest\"",
        "\"rrcConnectionReestablishment\"",
        "\"rrcConnectionReestablishmentReject\"",
        "\"rrcConnectionSetup\"",
        "\"rrcConnectionSetupComplete\"",
        "\"lte-rrc.nr_SecondaryCellGroupConfig_r15\"",
        "\"rrcConnectionReconfigurationComplete\"",
        "\"scgFailureInformationNR-r15\"",
        "\"nr-rrc.t304\"",
        "\"lte-rrc.t304\"",
        "\"nr-Config-r15: release (0)\"",
        "\"nr-Config-r15: setup (1)\"",
        "\"dualConnectivityPHR: setup (1)\"",
        "\"dualConnectivityPHR: release (0)\"",
        "\"nr-rrc.RRCReconfiguration_element\"",
        "nr-rrc.eventA",
        "\"nr-rrc.spCellConfig_element\"",
        "\"lte-rrc.targetPhysCellId\""
    ]

   
    while l:
        type_code = ["0"] * len(type_list)
        
        if "pair key" in l and r"</dm_log_packet>" in l:   #If the packet just have one line (5G RRC OTA packet)
            soup = BeautifulSoup(l, 'html.parser')
            timestamp = soup.find(key="timestamp").get_text()
            type_id = soup.find(key="type_id").get_text()
            try:
                PCI = soup.find(key="Physical Cell ID").get_text()
            except:
                PCI = "-"
            f2.write(",".join([timestamp, type_id, PCI, "-"] + type_code)+'\n')
            
            l = f.readline()
            continue
        
        elif "pair key" in l and r"</dm_log_packet>" not in l:  #If the packet has more than one line
            soup = BeautifulSoup(l, 'html.parser')
            timestamp = soup.find(key="timestamp").get_text()
            type_id = soup.find(key="type_id").get_text()
            try:
                PCI = soup.find(key="Physical Cell ID").get_text()
            except:
                PCI = "-"
            
            UL_DL = "-"
            nr_pci = "-"
            l = f.readline()
            
            while l and r"</dm_log_packet>" not in l:
                
                if "UL-DCCH-Message" in l:
                    UL_DL = "UL"
                if "DL-DCCH-Message" in l:
                    UL_DL = "DL"
                    
                if "nr-rrc.physCellId" in l:
                    nr_pci = l.split("\"")[9]
                    #print(nr_pci)
                
                c = 0
                for type in type_list:
                    if type in l:
                        type_code[c] = "1"
                    c += 1
                l = f.readline()
            f2.write(",".join([timestamp, type_id, PCI, UL_DL] + type_code + [nr_pci])+'\n')
        else:
            l = f.readline()
        

    f.close()
