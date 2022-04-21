#!/usr/bin/env python3

import socket
import time
import threading
import os
import datetime as dt
import argparse
import subprocess
import re
import signal

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=3237)
parser.add_argument("-b", "--bandwidth", type=float,
                    help="port to bind", default=300)

args = parser.parse_args()
print(args.port)
print(args.bandwidth)

IP_MTU_DISCOVER   = 10
IP_PMTUDISC_DONT  =  0  # Never send DF frames.
IP_PMTUDISC_WANT  =  1  # Use per route hints.
IP_PMTUDISC_DO    =  2  # Always DF.
IP_PMTUDISC_PROBE =  3  # Ignore dst pmtu.
TCP_CONGESTION = 13


HOST = '192.168.1.248'
PORT = args.port
PORT2 = args.port + 1
thread_stop = False
exit_program = False
length_packet = 250
bandwidth = args.bandwidth*1000
total_time = 3600
cong_algorithm = 'cubic'
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "/home/wmnlab/D/pcap_data"
ss_dir = "/home/wmnlab/D/ss"
hostname = str(PORT) + ":"
cong = cong_algorithm.encode()

def connection(host, port ,result):
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s_tcp.setsockopt(socket.SOL_IP, IP_MTU_DISCOVER, IP_PMTUDISC_DO)
    s_tcp.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong)

    s_tcp.bind((host, port))
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()
    result[0] = s_tcp, conn, tcp_addr

def get_ss(port):
    now = dt.datetime.today()
    n = str(port)+'_'+'-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    f = open(os.path.join(ss_dir, n)+".csv", 'a+')
    while not thread_stop:
        proc = subprocess.Popen(["ss -ai src :%d"%(port)], stdout=subprocess.PIPE, shell=True)
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline().decode().strip()
        f.write(",".join([str(dt.datetime.now())]+ re.split("[: \n\t]", line))+'\n')
        time.sleep(1)
    f.close()
def transmision(conn):
    print(PORT, "start transmision to addr", conn)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    redundent = os.urandom(length_packet-12-1)

    global thread_stop
    while time.time() - start_time < total_time and not thread_stop:
        try:
            t = time.time()
            t = int(t*1000).to_bytes(8, 'big')
            z = i.to_bytes(4, 'big')
            outdata = t + z + ok +redundent
            conn.sendall(outdata)
            i += 1
            time.sleep(sleeptime)
            if time.time()-start_time > count:
                #print("[%d-%d]"%(count-1, count), "transmit", i-prev_transmit)
                count += 1
                sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
                prev_transmit = i
                prev_sleeptime = sleeptime
        except:
            break    
    print(PORT, "---transmision timeout---")


    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(length_packet-8*3-1)
    outdata = t + z + ok +redundent
    conn.sendall(outdata)

    print("transmit", i, "packets")


def receive(conn):
    conn.settimeout(10)
    print(PORT, "wait for indata...")
    i = 0
    start_time = time.time()
    count = 1
    seq = 0
    prev_capture = 0
    prev_loss = 0
    recv_bytes = 0
    global thread_stop
    while not thread_stop:
        try:
            indata = conn.recv(65535)
            recv_bytes += len(indata)

            if not indata:
                print("close")
                break
            if time.time()-start_time > count:
                # print("[%d-%d]"%(count-1, count), recv_bytes*8/1024, "kbps")
                recv_bytes = 0
                count += 1
        except Exception as inst:
            print("Error: ", inst)
            thread_stop = True
    thread_stop = True
    print(PORT, "---Experiment Complete---")
    print(PORT, "STOP receiving")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))

if not os.path.exists(ss_dir):
    os.system("mkdir %s"%(ss_dir))


while not exit_program:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    try:
        # s_tcp, conn, tcp_addr = connection()
        pcapfile1 = "%s/DL_%s_%s.pcap"%(pcap_path, PORT, n)
        pcapfile2 = "%s/UL_%s_%s.pcap"%(pcap_path, PORT2, n)
        tcpproc =  subprocess.Popen(["tcpdump -i any port %s -w %s&"%(PORT, pcapfile1)], shell=True, preexec_fn=os.setsid)
        tcpproc2 =  subprocess.Popen(["tcpdump -i any port %s -w %s&"%(PORT2, pcapfile2)], shell=True, preexec_fn=os.setsid)

        result1 = [None]
        result2 = [None]
        connection_t1 = threading.Thread(target = connection, args = (HOST, PORT, result1)) # DL
        connection_t2 = threading.Thread(target = connection, args = (HOST, PORT2, result2)) # UL
        connection_t1.start()
        connection_t2.start()
        connection_t1.join()
        connection_t2.join()
        s_tcp1, conn1, tcp_addr1 = result1[0]
        s_tcp2, conn2, tcp_addr2 = result2[0]
    except KeyboardInterrupt:
        print("KeyboardInterrupt -> kill tcpdump")
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc2.pid), signal.SIGTERM)
        subprocess.Popen(["rm %s"%(pcapfile1)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile2)], shell=True)
        exit_program = True
        thread_stop = True
        break
    except Exception as inst:
        print("Connection Error:", inst)
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc2.pid), signal.SIGTERM)
        subprocess.Popen(["rm %s"%(pcapfile1)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile2)], shell=True)
        continue

    thread_stop = False
    t = threading.Thread(target = transmision, args = (conn1, )) 
    t1 = threading.Thread(target = receive, args = (conn2,))
    t2 = threading.Thread(target = get_ss, args = (PORT,))
    t3 = threading.Thread(target = get_ss, args = (PORT2,))
    t.start()
    t1.start()
    # t2.start()
    # t3.start()
    try:
        t.join()
        t1.join()
        # t2.join()
        # t3.join()
    except KeyboardInterrupt:
        print("finish")
        exit_program = True
    except Exception as inst:
        print("Error:", inst)
        print("finish")
    finally:
        thread_stop = True
        s_tcp1.close()
        s_tcp2.close()
        conn1.close()
        conn2.close()
        os.killpg(os.getpgid(tcpproc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc2.pid), signal.SIGTERM)
