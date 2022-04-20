#! /system/bin/sh

settings put global ntp_server time.stdtime.gov.tw
settings get global ntp_server
now=$(date +"%y-%m-%d-%H-%M-%S")
# uplink
/sbin/iperf3.9m1 -c 140.112.20.183 -p [uplink port] -u -V -t 10800 -l 250 -b 200k&
# downlink
/sbin/iperf3.9m1 -c 140.112.20.183 -p [downlink port] -u -V -R -t 10800 -l 250 -b 200k&
# capture file
/sbin/tcpdump -i any net 140.112.20.183 -w "/sdcard/dataset/${now}_[uplink port]_[downlink port].pcap"&
# /sbin/tcpdump -w "/storage/emulated/0/dataset"&

