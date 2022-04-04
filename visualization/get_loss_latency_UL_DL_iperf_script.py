import os
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import dpkt
import socket
from dpkt.compat import compat_ord
import enum
from pprint import pprint


# Using enum class to create enumerations
class Payload(enum.IntEnum):
    # !!! Define the length of each packet payload (bytes) !!!
    LENGTH = 250
class StrEnum(str, enum.Enum):
    pass
class Server(StrEnum):
    # !!! Define Server IP (Public/Private) !!!
    PUB_IP = '140.112.20.183'
    PVT_IP = '192.168.1.248'  # ifconfig

def to_utc8(ts):
    """Convert a timestamp to a readable type (at utc-8)
       
       Args:
           ts (float): timestamp composed of datetimedec + microsecond (e.g., 1644051509.989306)
       Returns:
           datetime.datetime: Readable timestamp (at utc-8)
    """
    return (dt.datetime.utcfromtimestamp(ts) + dt.timedelta(hours=8))

def mac_addr(address):
    """Convert a MAC address to a readable/printable string

       Args:
           address (str): a MAC address in hex form (e.g. '\x01\x02\x03\x04\x05\x06')
       Returns:
           str: Printable/readable MAC address
    """
    return ':'.join('%02x' % compat_ord(b) for b in address)

def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)

def overview_packets(pcap, N=50):
    """Get an overview of packets in pcap file

       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader)
           N (int): maximal display number (default: 50)
    """
    for i, (ts, buf) in enumerate(pcap):
        print(i+1)
        print("timestamp    :", ts)
        print("len_buf      :", len(buf))
        eth = dpkt.ethernet.Ethernet(buf)
        print("dpkt.ethernet.Ethernet")
        print("len_eth      :", len(eth))
        print("len_eth.data :", len(eth.data))
        print("type_eht.data:", type(eth.data))
        eth = dpkt.sll.SLL(buf)
        print("dpkt.sll.SLL")
        print("len_eth      :", len(eth))
        print("len_eth.data :", len(eth.data))
        print("type_eht.data:", type(eth.data))
        print()
        if i+1 == N:
            print('Maximal display number: %d. The remaining results are hidden.' % N)
            break

# Using enum class to create enumerations
class Flags(enum.Enum):
    ETH_DPKT_NEEDDATA = 1
    SLL_DPKT_NEEDDATA = 2
    ETH_NON_IP = 3
    SLL_NON_IP = 4
    SEQ_NOT_CONTI = 5
    SEQ_DUPL = 6

def print_packet(timestamp, buf, seq_set=set(), println=True):
    """Print out information about a packet
       
       Args:
           timestamp: timestamp of a packet in dpkt pcap reader object
           buf: content of a packets in dpkt pcap reader object
           seq_set: set of sequence numbers occured before
           println (bool): display the information or not
       Returns:
           flags (list): list of Exception/Error/Warning encountering
           seq_set: updated set of sequence numbers occured before
    """
    flags = []
    # Print out the timestamp in UTC
    if println:
        print('Timestamp: ', str(to_utc8(timestamp)))

    # Unpack the Ethernet frame (mac src/dst, ethertype)
    try:
        eth = dpkt.ethernet.Ethernet(buf)
        if println:
            print('Ethernet Frame: ', mac_addr(eth.src), mac_addr(eth.dst), eth.type)
    except dpkt.NeedData:
        if println:
            print('Warning: dpkt.NeedData (dpkt.ethernet.Ethernet), try dpkt.sll.SLL')
        eth = dpkt.sll.SLL(buf)
        flags.append((Flags.ETH_DPKT_NEEDDATA, ''))

    # Make sure the Ethernet data contains an IP packet
    if isinstance(eth, dpkt.ethernet.Ethernet):
        if not isinstance(eth.data, dpkt.ip.IP):
            if println:
                print('Non IP Packet type not supported %s, try dpkt.sll.SLL' % eth.data.__class__.__name__)
            flags.append((Flags.ETH_NON_IP, ''))
            eth = dpkt.sll.SLL(buf)
    if not isinstance(eth.data, dpkt.ip.IP):
        if println:
            print('Non IP Packet type not supported %s, forcing the data type into dpkt.ip.IP ' % eth.data.__class__.__name__)
        flags.append((Flags.SLL_NON_IP, ''))
        vlan_tag = dpkt.ethernet.VLANtag8021Q(eth.data[:4])
        ip = dpkt.ip.IP(eth.data[4:])
    else:
        # Now unpack the data within the Ethernet frame (the IP packet)
        # Pulling out src, dst, length, fragment info, TTL, and Protocol
        ip = eth.data

    # Pull out fragment information (flags and offset all packed into off field, so use bitmasks)
    do_not_fragment = bool(ip.off & dpkt.ip.IP_DF)
    more_fragments = bool(ip.off & dpkt.ip.IP_MF)
    fragment_offset = ip.off & dpkt.ip.IP_OFFMASK

    # Print out the info
    if println:
        print('IP: %s -> %s   (len=%d ttl=%d DF=%d MF=%d offset=%d)' % \
              (inet_to_str(ip.src), inet_to_str(ip.dst), ip.len, ip.ttl, do_not_fragment, more_fragments, fragment_offset))
    if (ip.len - (20+8)) % Payload.LENGTH == 0:
        udp = ip.data
        # udp.ulen: len( hdr(header)+pyl(payload) )
        if println:
            print('UDP: %d -> %d                   (len=%d pyl_len=%d)' % \
                  (udp.sport, udp.dport, udp.ulen, len(udp.data))) 
        clogged_num = len(udp.data) // Payload.LENGTH
        ofst = 0
        if clogged_num > 1:
            if println:
                print('     clogged')
        for i in range(clogged_num):
            datetimedec = int(udp.data.hex()[ofst+0:ofst+8], 16)
            microsec = int(udp.data.hex()[ofst+8:ofst+16], 16)
            pyl_time = str(to_utc8((datetimedec + microsec / 1e6)))
            seq = int(udp.data.hex()[ofst+16:ofst+24], 16)
            if println:
                print('     %s      (seq=%d)' % (pyl_time, seq))
            if (i > 0) and (seq != prev+1):
                if (inet_to_str(ip.dst) == Server.PUB_IP) or (inet_to_str(ip.dst) == Server.PVT_IP):
                    flags.append((Flags.SEQ_NOT_CONTI, (pyl_time, 'seq=%d' % seq, 'uplink')))
                else:
                    flags.append((Flags.SEQ_NOT_CONTI, (pyl_time, 'seq=%d' % seq, 'downlink')))
            if (pyl_time, seq) not in seq_set:
                seq_set.add((pyl_time, seq))
            else:
                if (inet_to_str(ip.dst) == Server.PUB_IP) or (inet_to_str(ip.dst) == Server.PVT_IP):
                    flags.append((Flags.SEQ_DUPL, (pyl_time, 'seq=%d' % seq, 'uplink')))
                else:
                    flags.append((Flags.SEQ_DUPL, (pyl_time, 'seq=%d' % seq, 'downlink')))
            ofst += (Payload.LENGTH*2)  # 1 byte == 2 hexadecimal digits
            prev = seq
    if println:
        print()
    return flags, seq_set

def print_packets(pcap, N=50, ano_display=False, M=50):
    """Print out information about each packet in the pcap reader

       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader)
           N (int): maximal display number (default: 50)
           ano_display (bool): display the index of anomalies in data or not
           M (int): maximal display number of anomalies display (default: 50)
    """
    print('=======================================================================')
    anomalies = {Flags.ETH_DPKT_NEEDDATA: [], 
                 Flags.SLL_DPKT_NEEDDATA: [], 
                 Flags.ETH_NON_IP: [], 
                 Flags.SLL_NON_IP: [],
                 Flags.SEQ_NOT_CONTI: [],
                 Flags.SEQ_DUPL: [],}
    # For each packet in the pcap process the contents
    seq_set = set()
    for i, (timestamp, buf) in enumerate(pcap):
        if i+1 <= N:
            print(i+1)
            flags, seq_set = print_packet(timestamp, buf, seq_set)
        else:
            flags, seq_set = print_packet(timestamp, buf, seq_set, False)
        for flag in flags:
            if flag[1]:
                anomalies[flag[0]].append((i+1, str(to_utc8(timestamp)), flag[1]))
            else:
                anomalies[flag[0]].append((i+1, str(to_utc8(timestamp))))
        if i+1 == N:
            print('Maximal display number: %d. The remaining results are hidden.\n' % N)

    if ano_display:
        print('------- Anomalies -------')
        for key, lst in anomalies.items():
            if lst:
                print(key)
                for i, item in enumerate(lst):
                    print(item)
                    if i+1 == M:
                        print('Maximal display number: %d. The remaining %d results are hidden.' % (M, len(lst)-M))
                        break
                print()
        print()

def get_loss_latency_UL(pcap):
    """Calculate latency of each arrived packet and analyze the packet loss events

       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader) for Server-side uplink data
       Returns:
           loss_timestamps (list): list of timestamps for each lost packet
           latency ([x, y]): transmission timestamp and latency for each arrived packet
    """

    # This for loop parse the payload of the iperf3 UDP packets and store the timestamps and the sequence numbers in timestamp_list; 
    # The timestamp is stored in the first 8 bytes, and the sequence number is stored in the 9~12 bytes
    # -------------------------------------------------------------------------------------------------
    timestamp_list = []
    seq_set = set()
    try:
        for i, (ts, buf) in enumerate(pcap):

            # Extract payload of the UDP packet
            # ---------------------------------
            try:
                eth = dpkt.ethernet.Ethernet(buf)
            except dpkt.NeedData:
                print('Warning: dpkt.NeedData (dpkt.ethernet.Ethernet)')
                continue
            # Here we set the length checking to be Payload.LENGTH * N + (20+8) to screen out the control messages
            if (len(eth.data) - (20+8)) % Payload.LENGTH != 0:
                continue

            # Unpack the data within the SLL frame (the IP packet)
            ip = eth.data
            udp = ip.data

            # ------------------------ only UL data left ------------------------
            # bug fix1: clogged packets | credit: JingYou | fixed by clogged_num
            # i.e., 一個 capture 之中，可能存在多個 payload 黏在一起傳（e.g., 250 * N）
            # bug fix2: duplicate packets | credit: JingYou | fixed by seq_set
            # i.e., 在不同時間點重複收到相同的 seq number （發送時間相同的 payload）
            #       但 UDP 理應不存在 retransmission，因此推斷為不合理的現象
            #       以初次收到的時間戳記為準，後續收到則忽略不計

            clogged_num = len(udp.data) // Payload.LENGTH
            ofst = 0
            for i in range(clogged_num):
                datetimedec = int(udp.data.hex()[ofst+0:ofst+8], 16)
                microsec = int(udp.data.hex()[ofst+8:ofst+16], 16)
                pyl_time = str(to_utc8(datetimedec + microsec/1e6))
                seq = int(udp.data.hex()[ofst+16:ofst+24], 16)
                # 若有中途重開 iperf3（seq number 重置為 1），推定此前的資料作廢，故重置 timestamp_list 和 seq_set
                # !!! 假定重開 iperf3 後的第一個 seq number 一定會收到，若沒收到不會重置 !!!
                # !!! 若想要保留重開 iperf3 之前的資料，則將下方三行註解掉，並修改 check packet loss 的 code !!!
                # calculate latency 的 code 應該不用修改，因為沒有倚靠 seq number
                # !!! 最好的做法為實驗時先開 tcpdump 再開 iperf3，若需要重開 iperf3，就兩個都重開 !!!
                if (seq == 1) and ((pyl_time, seq) not in seq_set):
                    timestamp_list = []
                    seq_set = set()
                if (pyl_time, seq) not in seq_set:
                    # timestamp 格式
                    # ts (float): pcap timestamp (e.g., 1644051509.989306)
                    # datetimedec (int): payload timestamp (e.g., 1644051509)
                    # microsec (int): payload timestamp (e.g., 989306)
                    # seq (int): payload sequence number (e.g., 1)
                    timestamp_list.append((ts, datetimedec, microsec, seq))
                    seq_set.add((pyl_time, seq))
                ofst += (Payload.LENGTH*2)  # 1 byte == 2 hexadecimal digits

    except dpkt.NeedData:
        print('Warning: dpkt.NeedData occurs when iterating pcap reader')
    
    # 由於前述的兩個處理，可以假定 seq number 不會重複出現，以 seq number 作排序
    # timestamp[0] 可能會重複（因為 clogged packets）
    timestamp_list = sorted(timestamp_list, key = lambda v : v[3])  # We consider out of order UDP packets

    # Checking packet loss...
    # ----------------------------------------------
    pointer = 1
    timestamp_store = None
    loss_timestamps = []

    count = 0
    for i, timestamp in enumerate(timestamp_list):
        # 只要存在於 timestamp_list 的封包，即為有收到的封包
        if timestamp[3] == pointer:
            # 收到的封包與預期的 seq number 相同（i.e., 期間內沒掉包）
            # timestamp_store = timestamp
            pass 
        else:
            if timestamp_store == None:
                # 若第一個封包就掉，無法預測此前的什麼時候掉，故不作紀錄
                # continue
                pass
            else:
                # 處理連續掉 1-N 個封包的狀況
                # timestamp_store 為前一刻收到的封包
                # timestamp 為此時此刻收到的封包
                # pointer 為預期收到的封包 seq（前一刻收到的 seq number + 1）
                # timestamp[3] 為此時此刻收到的封包 seq
                # timestamp[3]-pointer+2 == 遺漏的封包數+2（頭+尾），因此要去頭去尾才是實際遺漏的封包
                count += 1
                loss_linspace = np.linspace(timestamp_store, timestamp, timestamp[3]-pointer+2)
                loss_linspace = loss_linspace[1:-1]
                for item in loss_linspace:
                    loss_time = to_utc8(item[0])
                    loss_timestamps.append(loss_time)
        # Update
        timestamp_store = timestamp
        pointer = timestamp[3] + 1
        
    # x and y stands for the timestamp (x) and the one-way latency (y) on the timestamp, respectively
    # ----------------------------------------------
    x = []
    y = []
    for i in range(len(timestamp_list)):
        # Uplink: 觀察手機端發送封包的狀況
        transmitted_time = to_utc8(timestamp_list[i][1] + timestamp_list[i][2]/1e6)
        x.append(transmitted_time)
        # latency (convert into millisecond)
        y.append(((timestamp_list[i][0]+3600*8) - (timestamp_list[i][1]+timestamp_list[i][2]/1e6+3600*8)) * 1000)
    
    print("Uplink (UE => Server)")
    print("number of packets", len(timestamp_list))
    print("number of packet loss events", count)
    print("number of lost packets", len(loss_timestamps))
    if len(timestamp_list):
        print("packet loss rate", len(loss_timestamps) / len(timestamp_list) * 100, "%")
    print()

    latency = [x,y]    
    return loss_timestamps, latency

def get_loss_latency_DL(pcap):
    """Calculate latency of each arrived packet and analyze the packet loss events

       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader) for UE-side data
       Returns:
           loss_timestamps (list): list of timestamps for each lost packet
           latency ([x, y]): arrival timestamp and latency for each arrived packet
    """

    # This for loop parse the payload of the iperf3 UDP packets and store the timestamps and the sequence numbers in timestamp_list; 
    # The timestamp is stored in the first 8 bytes, and the sequence number is stored in the 9~12 bytes
    # -------------------------------------------------------------------------------------------------
    timestamp_list = []
    seq_set = set()
    try:
        for i, (ts, buf) in enumerate(pcap):

            # Extract payload of the UDP packet
            # ---------------------------------
            eth = dpkt.sll.SLL(buf)
            # Here we set the length checking to be Payload.LENGTH * N + (20+8+4) to screen out the control messages
            if (len(eth.data) - (20+8+4)) % Payload.LENGTH != 0:
                continue

            # Unpack the data within the SLL frame (the IP packet)
            if not isinstance(eth.data, dpkt.ip.IP):
                vlan_tag = dpkt.ethernet.VLANtag8021Q(eth.data[:4])
                ip = dpkt.ip.IP(eth.data[4:])
            else:
                ip = eth.data
            udp = ip.data
            
            # Neglect uplink data
            if inet_to_str(ip.dst) == Server.PUB_IP:
                continue
            
            # ------------------------ only DL data left ------------------------
            # bug fix1: clogged packets | credit: JingYou | fixed by clogged_num
            # i.e., 一個 capture 之中，可能存在多個 payload 黏在一起傳（e.g., 250 * N）
            # bug fix2: duplicate packets | credit: JingYou | fixed by seq_set
            # i.e., 在不同時間點重複收到相同的 seq number （發送時間相同的 payload）
            #       但 UDP 理應不存在 retransmission，因此推斷為不合理的現象
            #       以初次收到的時間戳記為準，後續收到則忽略不計
            
            clogged_num = len(udp.data) // Payload.LENGTH
            ofst = 0
            for i in range(clogged_num):
                datetimedec = int(udp.data.hex()[ofst+0:ofst+8], 16)
                microsec = int(udp.data.hex()[ofst+8:ofst+16], 16)
                pyl_time = str(to_utc8(datetimedec + microsec/1e6))
                seq = int(udp.data.hex()[ofst+16:ofst+24], 16)
                # 若有中途重開 iperf3（seq number 重置為 1），推定此前的資料作廢，故重置 timestamp_list 和 seq_set
                # !!! 假定重開 iperf3 後的第一個 seq number 一定會收到，若沒收到不會重置 !!!
                # !!! 若想要保留重開 iperf3 之前的資料，則將下方三行註解掉，並修改 check packet loss 的 code !!!
                # calculate latency 的 code 應該不用修改，因為沒有倚靠 seq number
                # !!! 最好的做法為實驗時先開 tcpdump 再開 iperf3，若需要重開 iperf3，就兩個都重開 !!!
                if (seq == 1) and ((pyl_time, seq) not in seq_set):
                    timestamp_list = []
                    seq_set = set()
                if (pyl_time, seq) not in seq_set:
                    # timestamp 格式
                    # ts (float): pcap timestamp (e.g., 1644051509.989306)
                    # datetimedec (int): payload timestamp (e.g., 1644051509)
                    # microsec (int): payload timestamp (e.g., 989306)
                    # seq (int): payload sequence number (e.g., 1)
                    timestamp_list.append((ts, datetimedec, microsec, seq))
                    seq_set.add((pyl_time, seq))
                ofst += (Payload.LENGTH*2)  # 1 byte == 2 hexadecimal digits

    except dpkt.NeedData:
        print('Warning: dpkt.NeedData occurs when iterating pcap reader')

    # 由於前述的兩個處理，可以假定 seq number 不會重複出現，以 seq number 作排序
    # timestamp[0] 可能會重複（因為 clogged packets）
    timestamp_list = sorted(timestamp_list, key = lambda v : v[3])  # We consider out of order UDP packets

    # Checking packet loss...
    # ----------------------------------------------
    pointer = 1
    timestamp_store = None
    loss_timestamps = []

    count = 0
    for i, timestamp in enumerate(timestamp_list):
        # 只要存在於 timestamp_list 的封包，即為有收到的封包
        if timestamp[3] == pointer:
            # 收到的封包與預期的 seq number 相同（i.e., 期間內沒掉包）
            # timestamp_store = timestamp
            pass 
        else:
            if timestamp_store == None:
                # 若第一個封包就掉，無法預測此前的什麼時候掉，故不作紀錄
                # continue
                pass
            else:
                # 處理連續掉 1-N 個封包的狀況
                # timestamp_store 為前一刻收到的封包
                # timestamp 為此時此刻收到的封包s
                # pointer 為預期收到的封包 seq（前一刻收到的 seq number + 1）
                # timestamp[3] 為此時此刻收到的封包 seq
                # timestamp[3]-pointer+2 == 遺漏的封包數+2（頭+尾），因此要去頭去尾才是實際遺漏的封包
                count += 1
                loss_linspace = np.linspace(timestamp_store, timestamp, timestamp[3]-pointer+2)
                loss_linspace = loss_linspace[1:-1]
                for item in loss_linspace:
                    loss_time = to_utc8(item[0])
                    loss_timestamps.append(loss_time)
        # Update
        timestamp_store = timestamp
        pointer = timestamp[3] + 1
        
    # x and y stands for the timestamp (x) and the one-way latency (y) on the timestamp, respectively
    # ----------------------------------------------
    x = []
    y = []
    # !!! 之前 Server 的 iperf3 出事，導致 Server 產生的 payload 發送時間都變成 1970 年出生 !!!
    # 因此只能取第一個封包的 latency 為基準進行調整（但若第一個封包的 latency 太長，分析可能會失準）
    # 由於出事的是 Server 作為發送端的情況，因此只有分析 downlink 的 payload 時要處理
    const_dif = 0
    if to_utc8(timestamp_list[0][1]).year == 1970:
        print("Warning: payload timestamps were recorded as year 1970")
        const_dif = timestamp_list[0][0]+3600*8 - (timestamp_list[0][1]+timestamp_list[0][2]/1e6+3600*8) 
    for i in range(len(timestamp_list)):
        # Downlink: 觀察手機端接收封包的狀況
        arrival_time = to_utc8(timestamp_list[i][0])
        x.append(arrival_time)
        # latency (convert into millisecond)
        y.append(((timestamp_list[i][0]+3600*8) - (timestamp_list[i][1]+timestamp_list[i][2]/1e6+3600*8) - const_dif) * 1000)
    
    print("Downlink (Server => UE)")
    print("number of packets", len(timestamp_list))
    print("number of packet loss events", count)
    print("number of lost packets", len(loss_timestamps))
    if len(timestamp_list):
        print("packet loss rate", len(loss_timestamps) / len(timestamp_list) * 100, "%")
    print()

    latency = [x,y]    
    return loss_timestamps, latency

if __name__ == "__main__":
    cell_phone_file = "/Users/jackbedford/Documents/Workspace/MOXA/src/testdata/data/中華/22-02-05-16-49-30_3235_3236.pcap"
    server_UL_file = "/Users/jackbedford/Documents/Workspace/MOXA/src/testdata/data/中華/2022-2-5-16-47-41_serverDump_3235_UL.pcap"
    server_DL_file = "/Users/jackbedford/Documents/Workspace/MOXA/src/testdata/data/中華/2022-2-5-16-47-41_serverDump_3236_DL.pcap"

    f = open(cell_phone_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    # overview_packets(pcap)
    print_packets(pcap, ano_display=True)
    # print_packets(pcap, 1000000, ano_display=True)

    f = open(server_UL_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    # overview_packets(pcap)
    print_packets(pcap, ano_display=True)
    # print_packets(pcap, 1000000, ano_display=True)

    f = open(server_DL_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    # overview_packets(pcap)
    print_packets(pcap, ano_display=True)
    # print_packets(pcap, 1000000, ano_display=True)

    # 透過以上觀察，可以大致掌握到以下的結論：
    # UE 端的 data 需要用 dpkt.sll.SLL() 來解析，且 eth.data 不含 dpkt.ip.IP
    # 因此，若確定每個 capture 只包含 IP packets，則可以直接將 data type 從 'byte' 強制轉為 'dpkt.ip.IP'
    # >>> ip = dpkt.ip.IP(eth.data[4:])
    # Server 端的 data 則要用 dpkt.ethernet.Ethernet 解析
    # 由於 eth.data 含有 dpkt.ip.IP，因此可以直接調用 eth.data
    # >>> ip = eth.data
    # 對於同一個封包，兩者得到的 ip.len, ip.tll 等理應相同
    # 若沒有中途重開 iperf3，對於同一個 seq number，其生成時間（發送時間）理應相同

    # simple drawing...
    fig , ax = plt.subplots(2, 1, sharex=True, sharey=False)

    f = open(server_UL_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    UL_loss_timestamps, UL_latency = get_loss_latency_UL(pcap)

    f = open(cell_phone_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    DL_loss_timestamps, DL_latency = get_loss_latency_DL(pcap)

    plt.subplot(2,1,1)
    plt.gca().set_title('Uplink')
    plt.plot(UL_latency[0], UL_latency[1], c='blue')
    for loss_time in UL_loss_timestamps:
        plt.axvline(loss_time, c='red')

    plt.subplot(2,1,2)
    plt.gca().set_title('Downlink')
    plt.plot(DL_latency[0], DL_latency[1], c='blue')
    for loss_time in DL_loss_timestamps:
        plt.axvline(loss_time, c='red')

    plt.show()