#! /system/bin/sh


settings put global ntp_server time.stdtime.gov.tw
settings get global ntp_server
now=$(date +"%y-%m-%d-%H-%M-%S")
/bin/iperf3 -c 140.112.20.183 -p 3235 -V -u -t 3600 -l 250 -b 200k&
/bin/iperf3 -c 140.112.20.183 -p 3236 -R -u -V -t 3600 -l 250 -b 200k&
/bin/tcpdump -i any net 140.112.20.183 -w "/sdcard/dataset/${now}.pcap"&
# /sbin/tcpdump -w "/storage/emulated/0/dataset"&


