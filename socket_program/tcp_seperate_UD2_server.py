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
parser.add_argument("-p1", "--port1", type=int,
                    help="port to bind", default=3237)
parser.add_argument("-p2", "--port2", type=int,
                    help="port to bind", default=3238)
args = parser.parse_args()

IP_MTU_DISCOVER   = 10
IP_PMTUDISC_DONT  =  0  # Never send DF frames.
IP_PMTUDISC_WANT  =  1  # Use per route hints.
IP_PMTUDISC_DO    =  2  # Always DF.
IP_PMTUDISC_PROBE =  3  # Ignore dst pmtu.
TCP_CONGESTION = 13


HOST = '192.168.1.248'
PORT = args.port1           # UL
PORT2 = args.port2          # UL
PORT3 = args.port1 + 10     # DL
PORT4 = args.port2 + 10     # DL

thread_stop = False
exit_program = False
length_packet = 362
bandwidth = 289.6*1000*10
total_time = 3600
cong_algorithm = 'cubic'
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "/home/wmnlab/D/pcap_data2"
ss_dir = "/home/wmnlab/D/ss"
hostname = str(PORT) + ":"

cong = 'reno'.encode()

def connection(host, port, result):
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s_tcp.setsockopt(socket.SOL_IP, IP_MTU_DISCOVER, IP_PMTUDISC_DO)
    s_tcp.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong)
    s_tcp.bind((host, port))
    print((host, port), "wait for connection...")
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()
    print((host, port), "connection setup complete")
    result[0] = s_tcp, conn, tcp_addr

def get_ss(port):
    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    f = open(os.path.join(ss_dir, n)+'.csv', 'a+')
    while not thread_stop:
        proc = subprocess.Popen(["ss -ai dst :%d"%(port)], stdout=subprocess.PIPE, shell=True)
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline().decode().strip()
        f.write(",".join([str(dt.datetime.now())]+ re.split("[: \n\t]", line))+'\n')
        time.sleep(1)
    f.close()

def transmision(conn1, conn2):
    print("start transmision to addr", conn1)
    print("start transmision to addr", conn2)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    global thread_stop
    while time.time() - start_time < total_time and not thread_stop:
        try:
            t = time.time()
            datetimedec = int(t)
            microsec = int(str(t - int(t))[2:10])
            z = i.to_bytes(8, 'big')
            redundent = os.urandom(length_packet-8*3-1)
            outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
            conn1.sendall(outdata)
            conn2.sendall(outdata)
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
    print("---transmision timeout---")


    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(length_packet-8*3-1)
    outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
    conn1.sendall(outdata)
    conn2.sendall(outdata)

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
            duplicate_num = len(indata) // length_packet
            if len(indata) % length_packet != 0:
                i += 1
                continue                
            for j in range(duplicate_num):
                seq = int(indata[16+j*length_packet:24+j*length_packet].hex(), 16)
                # ts = int(int(indata[0:8].hex(), 16)) + float("0." + str(int(indata[8:16].hex(), 16)))
                # print(dt.datetime.fromtimestamp(time.time())-dt.datetime.fromtimestamp(ts)-dt.timedelta(seconds=0.28))
                # s_local.sendall(indata)
                ok = int(indata[24+j*length_packet:25+j*length_packet].hex(), 16)
                if ok == 0:
                    break
                else:
                    i += 1
            if time.time()-start_time > count:
                print("[%d-%d]"%(count-1, count), "capture", i-prev_capture)
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

if not os.path.exists(ss_dir):
    os.system("mkdir %s"%(ss_dir))


while not exit_program:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])

    pcapfile1 = "%s/UL_%s_%s.pcap"%(pcap_path, PORT, n)
    pcapfile2 = "%s/UL_%s_%s.pcap"%(pcap_path, PORT2, n)
    pcapfile3 = "%s/DL_%s_%s.pcap"%(pcap_path, PORT3, n)
    pcapfile4 = "%s/DL_%s_%s.pcap"%(pcap_path, PORT4, n)


    tcpproc1 =  subprocess.Popen(["tcpdump -i any port %s -w %s &"%(PORT,  pcapfile1)], shell=True, preexec_fn=os.setsid)
    tcpproc2 =  subprocess.Popen(["tcpdump -i any port %s -w %s &"%(PORT2, pcapfile2)], shell=True, preexec_fn=os.setsid)
    tcpproc3 =  subprocess.Popen(["tcpdump -i any port %s -w %s &"%(PORT3, pcapfile3)], shell=True, preexec_fn=os.setsid)
    tcpproc4 =  subprocess.Popen(["tcpdump -i any port %s -w %s &"%(PORT4, pcapfile4)], shell=True, preexec_fn=os.setsid)
    time.sleep(1)
    try:
        result1 = [None]
        result2 = [None]
        result3 = [None]
        result4 = [None]
        connection_t1 = threading.Thread(target = connection, args = (HOST, PORT, result1))  # UE1 UL
        connection_t2 = threading.Thread(target = connection, args = (HOST, PORT2, result2)) # UE2 UL
        connection_t3 = threading.Thread(target = connection, args = (HOST, PORT3, result3)) # UE1 DL
        connection_t4 = threading.Thread(target = connection, args = (HOST, PORT4, result4)) # UE2 DL
        connection_t1.start()
        connection_t2.start()
        connection_t3.start()
        connection_t4.start()
        connection_t1.join()
        connection_t2.join()
        connection_t3.join()
        connection_t4.join()
        s_tcp1, conn1, tcp_addr1 = result1[0]
        s_tcp2, conn2, tcp_addr2 = result2[0]
        s_tcp3, conn3, tcp_addr3 = result3[0]
        s_tcp4, conn4, tcp_addr4 = result4[0]
    except KeyboardInterrupt:
        print("KeyboardInterrupt -> kill tcpdump")
        os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc2.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc3.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc4.pid), signal.SIGTERM)
        subprocess.Popen(["rm %s"%(pcapfile1)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile2)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile3)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile4)], shell=True)
        exit_program = True
        thread_stop = True
        break

    except Exception as inst:
        print("Connection Error:", inst)
        os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc2.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc3.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc4.pid), signal.SIGTERM)
        subprocess.Popen(["rm %s"%(pcapfile1)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile2)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile3)], shell=True)
        subprocess.Popen(["rm %s"%(pcapfile4)], shell=True)

        continue
    conn1.sendall(b"START")
    conn2.sendall(b"START")
    conn3.sendall(b"START")
    conn4.sendall(b"START")
    time.sleep(0.5)
    thread_stop = False
    t = threading.Thread(target = transmision, args = (conn3, conn4))
    t1 = threading.Thread(target = receive, args = (conn1,))
    t2 = threading.Thread(target = receive, args = (conn2,))
    t3 = threading.Thread(target = get_ss, args = (PORT,))
    t4 = threading.Thread(target = get_ss, args = (PORT2,))
    t5 = threading.Thread(target = get_ss, args = (PORT3,))
    t6 = threading.Thread(target = get_ss, args = (PORT4,))
    t.start()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    try:
        t.join()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
    except KeyboardInterrupt:
        print("finish")
    except Exception as inst:
        print("Error:", inst)
        print("finish")
    finally:
        thread_stop = True
        s_tcp1.close()
        s_tcp2.close()
        s_tcp3.close()
        s_tcp4.close()
        conn1.close()
        conn2.close()
        conn3.close()
        conn4.close()
        os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc2.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc3.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc4.pid), signal.SIGTERM)
