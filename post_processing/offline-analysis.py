import os
import sys

"""
Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer, WcdmaRrcAnalyzer, LteNasAnalyzer, UmtsNasAnalyzer, LtePhyAnalyzer, LteMacAnalyzer, NrRrcAnalyzer

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    
    dirpath = sys.argv[1]
    filenames = os.listdir(dirpath)
    for each_file in filenames:
        print(each_file)
        path = sys.argv[1] + each_file
        
        src = OfflineReplayer()
        
        
        # src.set_input_path("./logs/diag_log_20210830_185225_aaa4dc12971e6450aedde3a6ea3adb20_Xiaomi-M2007J3SY_46692.mi2log")
        
        
        print("path", path)
        src.set_input_path(path)
        # src.set_input_path("./diag_log_20210830_185225_aaa4dc12971e6450aedde3a6ea3adb20_Xiaomi-M2007J3SY_46692.mi2log")
        
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as(path+".txt")
        logger.set_source(src)
        
        # Analyzers
        lte_rrc_analyzer = LteRrcAnalyzer()
        lte_rrc_analyzer.set_source(src)  # bind with the monitor
        
        nr_rrc_analyzer = NrRrcAnalyzer()
        nr_rrc_analyzer.set_source(src)
        
        wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
        wcdma_rrc_analyzer.set_source(src)  # bind with the monitor
        
        #lte_nas_analyzer = LteNasAnalyzer()
        #lte_nas_analyzer.set_source(src)
        
        #umts_nas_analyzer = UmtsNasAnalyzer()
        #umts_nas_analyzer.set_source(src)
        
        #lte_phy_analyzer = LtePhyAnalyzer()
        #lte_phy_analyzer.set_source(src)
        
        #lte_mac_analyzer = LteMacAnalyzer()
        #lte_mac_analyzer.set_source(src)
        
        # Start the monitoring
        src.run()
