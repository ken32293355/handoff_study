#!/usr/bin/env python3

# from asyncio import subprocess
import socket
import time
import threading
import os
import datetime as dt
import argparse
import subprocess
from typing import final

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=3237)
args = parser.parse_args()
print(args.port)

IP_MTU_DISCOVER   = 10
IP_PMTUDISC_DONT  =  0  # Never send DF frames.
IP_PMTUDISC_WANT  =  1  # Use per route hints.
IP_PMTUDISC_DO    =  2  # Always DF.
IP_PMTUDISC_PROBE =  3  # Ignore dst pmtu.

HOST = '192.168.1.248'
PORT = args.port
PORT = 3233
thread_stop = False
exit_program = False
length_packet = 362
bandwidth = 200*1000
total_time = 3600
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "pcapdir"

hostname = str(PORT) + ":"

def connection():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s_tcp.setsockopt(socket.IPPROTO_IP, socket.IP_DONTFRAG, 1)

    s_tcp.setsockopt(socket.SOL_IP, IP_MTU_DISCOVER, IP_PMTUDISC_DONT)

    s_tcp.bind((HOST, PORT))
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()

    return s_tcp, conn, tcp_addr

def remote_control(conn, t):
    global thread_stop
    global exit_program
    
    while t.is_alive() and not thread_stop:
        try:
            print("waiting for stopping")
            indata, addr = conn.recvfrom(1024)
            print('recvfrom ' + str(addr) + ': ' + indata.decode())
            if not indata or indata.decode() == "STOP" or not addr:
                thread_stop = True
                break
        except Exception as inst:
            print("Error: ", inst)
    print("STOP remote control")

def transmision(conn):
    print("start transmision to addr", conn)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    while time.time() - start_time < total_time and not thread_stop:
        t = time.time()
        datetimedec = int(t)
        microsec = int(str(t - int(t))[2:10])
        z = i.to_bytes(8, 'big')
        redundent = os.urandom(length_packet-8*3-1)
        outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
        conn.sendall(outdata)
        i += 1
        time.sleep(sleeptime)
        if time.time()-start_time > count:
            #print("[%d-%d]"%(count-1, count), "transmit", i-prev_transmit)
            count += 1
            sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
            prev_transmit = i
            prev_sleeptime = sleeptime
    
    print("---transmision timeout---")


    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(length_packet-8*3-1)
    outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
    conn.sendall(outdata)

    print("transmit", i, "packets")


def receive(conn):
    conn.settimeout(3)
    print("wait for indata...")
    i = 0
    start_time = time.time()
    count = 1
    seq = 0
    prev_capture = 0
    prev_loss = 0
    global thread_stop
    while not thread_stop:
        try:
            indata = conn.recv(65535)
            if not indata:
                print("close")
                break
            elif len(indata) != length_packet:
                print("WTF len", len(indata))
            seq = int(indata[16:24].hex(), 16)
            ts = int(int(indata[0:8].hex(), 16)) + float("0." + str(int(indata[8:16].hex(), 16)))
            # print(dt.datetime.fromtimestamp(time.time())-dt.datetime.fromtimestamp(ts)-dt.timedelta(seconds=0.28))
            # s_local.sendall(indata)
            ok = int(indata[24:25].hex(), 16)
            # buffer.put(indata)
            if ok == 0:
                break
            else:
                i += 1
            if time.time()-start_time > count:
                print("[%d-%d]"%(count-1, count), "capture", i-prev_capture, "loss", seq-i+1-prev_loss, sep='\t')
                prev_loss += seq-i+1-prev_loss
                count += 1
                prev_capture = i
        except Exception as inst:
            print("Error: ", inst)
            thread_stop = True
    thread_stop = True
    print("[%d-%d]"%(count-1, count), "capture", i-prev_capture, "loss", seq-i+1-prev_loss, sep='\t')
    print("---Experiment Complete---")
    print("Total capture: ", i, "Total lose: ", seq - i + 1)
    print("STOP bypass")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))


# os.system("kill -9 $(ps -A | grep python | awk '{print $1}')") 

while not exit_program:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    #os.system("echo wmnlab | sudo -S pkill tcpdump")
    # os.system("echo wmnlab | sudo -S tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT, pcap_path,PORT, n))
    tcpproc =  subprocess.Popen(["tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT, pcap_path,PORT, n)], shell=True)
    time.sleep(1)
    try:
        s_tcp, conn, tcp_addr = connection()
    except Exception as inst:
        print("Connection Error:", inst)
        continue
    thread_stop = False
    # t = threading.Thread(target = transmision, args = (conn, ))
    t1 = threading.Thread(target = receive, args = (conn,))

    # t.start()
    t1.start()
    try:
        # t.join()
        t1.join()
    except KeyboardInterrupt:
        print("finish1")
    except Exception as inst:
        print("Error:", inst)
        print("finish2:", inst)
    finally:
        thread_stop = True
        s_tcp.close()
        conn.close()
        tcpproc.terminate()