#!/usr/bin/env python3

import socket
import time
import threading
import os
import datetime as dt
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=3237)
args = parser.parse_args()
print(args.port)



HOST = '192.168.1.248'
PORT = args.port
thread_stop = False
exit_program = False
length_packet = 250
bandwidth = 2000*1000
total_time = 3600
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "pcapdir"

hostname = str(PORT) + ":"

def connection():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_tcp.bind((HOST, PORT))
    s_udp.bind((HOST, PORT))

    udp_addr = ""
    # s_tcp.listen()
    # print("wait for tcp connection...")
    # conn, tcp_addr = s_tcp.accept()
    # print('tcp Connected by', tcp_addr)
    # print("wait for udp say hi...")
    # indata, udp_addr = s_udp.recvfrom(1024)
    # print('udp Connected by', udp_addr)
    # print('server start at: %s:%s' % (HOST, PORT))

    ###
    s_udp.settimeout(0)
    print("reading trash...")
    while True:
        try:
            print("reading trash...")
            indata, udp_addr = s_udp.recvfrom(1024)
        except:
            break

    s_udp.settimeout(3)

    ### PHASE1 TCP connection establishment

    print(hostname, "wait for tcp connection...")
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()
    print(hostname, 'tcp Connected by', tcp_addr)


    ### PHASE2 UDP1 connection establishment

    print(hostname, "wait for udp say 123...")
    try:
        indata, udp_addr = s_udp.recvfrom(1024)
    except:
        pass
    while True:
        try:
            if indata.decode() == "123":
                conn.sendall(b"PHASE2 OK")
                break

            else:
                print("get", indata.decode(), "wrong")
        except Exception as inst:
            print("Error: ", inst)
        try:
            indata, udp_addr = s_udp.recvfrom(1024)
        except:
            pass
    print('udp Connected by', udp_addr)
    print('udp say', indata)
    print("wait for client say OK...")

    try:
        indata = conn.recv(65535)
        if indata == b'OK':
            print("connection setup complete")
        else:
            print("connection setup fail")
            return 0
    except:
        exit(1)


    return s_tcp, s_udp, conn, tcp_addr, udp_addr

def remote_control(conn, t):
    global thread_stop
    global exit_program
    while t.is_alive():
        try:
            print("waiting for stopping")
            indata, addr = conn.recvfrom(1024)
            print('recvfrom ' + str(addr) + ': ' + indata.decode())
            if not indata or indata.decode() == "STOP" or not addr:
                thread_stop = True
                break
            elif indata.decode() == "EXIT":
                thread_stop = True
                exit_program = True
                break
        except Exception as inst:
            print("Error: ", inst)
    print("STOP remote control")

def transmision(s_udp, conn, udp_addr):
    print("start transmision to addr", udp_addr)
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
        redundent = os.urandom(250-8*3-1)
        outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
        s_udp.sendto(outdata, udp_addr)
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
    redundent = os.urandom(250-8*3-1)
    outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
    s_udp.sendto(outdata, udp_addr)

    print("transmit", i, "packets")


def bybass_rx(s_udp):
    s_udp.settimeout(3)
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
            indata, addr = s_udp.recvfrom(1024)
            if len(indata) != 250:
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
    os.system("echo wmnlab | sudo -S pkill tcpdump")
    os.system("echo wmnlab | sudo -S tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT, pcap_path,PORT, n))
    time.sleep(2)
    try:
        s_tcp, s_udp, conn, tcp_addr, udp_addr = connection()
    except Exception as inst:
        print("Connection Error:", inst)
        continue
    thread_stop = False
    t = threading.Thread(target = transmision, args = (s_udp, conn, udp_addr))
    t1 = threading.Thread(target = bybass_rx, args = (s_udp,))
    t2 = threading.Thread(target = remote_control, args = (conn, t))

    t.start()
    t1.start()
    t2.start()
    
    t.join()
    t1.join()
    t2.join()
    s_tcp.close()

    s_udp.settimeout(0)
    print("reading trash...")
    while True:
        try:
            print("reading trash...")
            indata, udp_addr = s_udp.recvfrom(1024)
        except:
            break


    s_udp.close()
    conn.close()
    os.system("echo wmnlab | sudo -S pkill tcpdump")
