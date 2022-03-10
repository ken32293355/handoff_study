### a. 操作流程

Note: 操作順序需先運行 server 上之 `iperf_server_for_class.py` ，才能運行手機上之 script files

#### a.1 Start

All supported port: 3200-3300, odd number for Uplink, even number for Downlink.

You may type:

(1) `sudo python3 iperf_server_for_class.py start 3231` to open port 3231-3232. 

(2) `sudo python3 iperf_server_for_class.py start 3235 3237 3231` to open port 3231-3232 & 3235-3238.
 
