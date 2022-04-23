# change cong
echo reno > /proc/sys/net/ipv4/tcp_congestion_control
# check current
cat /proc/sys/net/ipv4/tcp_congestion_control
# list all cong
grep TCP_CONG /boot/config-$(uname -r)

