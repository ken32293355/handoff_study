# Handoff_study

## 1. Script tools for iperf3, tcpdump

存放位置: `script_ss/` (for samsung cell phone), `utils/iperf_server_for_class.py` (for server)

Purpose: 以 script 型式一鍵執行 iperf3, tcpdump 等封包傳輸、封包收集工具

## 2. Processing tools for Mobile Insight

存放位置: `post_processing/offline_analysis.py`, `post_processing/xml_mi.py`

Purpose: offline_analysis.py 可以將 Mobile Insight 的 raw data decode 為 .txt file 

xml_mi.py 則可以將 .txt file 中想抓取的資訊提取出來製作成 .csv file
 
## 3. 基地台訊號量測、GPS 位置紀錄 APP (self-developed)

存放位置: `APP Source Code/cellInfoMonitor`

Purpose: 紀錄基地台訊號等資訊，並儲存資訊成檔案以利後續分析

可以在手機螢幕上知道該秒服務手機的基地台以及訊號強度、GPS 位置等資訊。

Note: 之後檔案需用 `post_processing/cell_info_csv_processing.py` 做處理



