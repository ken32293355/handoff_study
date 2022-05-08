import datetime as dt
from statistics import mean
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from tqdm import tqdm
from joblib import Parallel, delayed

length_packet = 362

def rtt_plot(pcap_csv):
    df = pd.read_csv(pcap_csv, sep='@')
    df.loc[:, "frame.time"] = pd.to_datetime(df.loc[:, r"frame.time"]).dt.tz_localize(None)
    df = df[np.invert(np.isnan(df.loc[:, "tcp.analysis.ack_rtt"]))]
    df.reset_index(inplace=True)
    # df.plot(df.loc[:, "frame.time"], df.loc[:, "tcp.analysis.ack_rtt"])
    # plt.show()
    plt.xlabel("time")
    plt.ylabel("second")
    plt.plot(df.loc[:, "frame.time"], df.loc[:, "tcp.analysis.ack_rtt"])
    plt.show()

def rtt(pcap_csv, pcap_csv2):

    df = pd.read_csv(pcap_csv, sep='@')
    df.loc[:, "frame.time"] = pd.to_datetime(df.loc[:, r"frame.time"]).dt.tz_localize(None)

    df2 = pd.read_csv(pcap_csv2, sep='@')
    df2.loc[:, "frame.time"] = pd.to_datetime(df2.loc[:, r"frame.time"]).dt.tz_localize(None)

    begin_time = max(df.loc[0, "frame.time"], df2.loc[0, "frame.time"])
    end_time = min(df.loc[len(df)-1, "frame.time"], df2.loc[len(df2)-1, "frame.time"])
    
    df = df[(df.loc[:, "frame.time"] >= begin_time) & (df.loc[:, "frame.time"] <= end_time)]
    df2 = df2[(df2.loc[:, "frame.time"] >= begin_time) & (df2.loc[:, "frame.time"] <= end_time)]
    
    df['rtt'] = 0.0
    df2['rtt'] = 0.0
    
    df.reset_index(inplace=True)
    df2.reset_index(inplace=True)

    frame_seq_dict = {}
    max_seq = 0
    
    df_lost = 0
    df2_lost = 0

    print("maping frame to eqch seq...")
    # map frame to eqch seq
    for i in tqdm(range(len(df))):
        if df.loc[i, "tcp.len"] > 0 and df.loc[i, "tcp.len"] % length_packet == 0:
            dup_num = df.loc[i, "tcp.len"] // length_packet
            frame_num = df.loc[i, "frame.number"]
            frame_seq_dict[frame_num] = []
            for j in range(dup_num):
                seq = int(df.loc[i, "tcp.payload"][32+j*length_packet*2:48+j*length_packet*2], 16)
                frame_seq_dict[frame_num].append(seq)
                max_seq = seq
        elif df.loc[i, "tcp.len"] > 0 and df.loc[i, "tcp.len"] % length_packet != 0:
            df_lost += 1
    # map rtt to each frame
    print("maping rtt to each frame...")
    # df.loc[df.loc[:, "tcp.analysis.acks_frame"], "rtt"] = df.loc[:, "tcp.analysis.ack_rtt"]


    for i in tqdm(range(len(df))):
        if df.loc[i, "tcp.analysis.acks_frame"]:
            df.loc[df.loc[i, "tcp.analysis.acks_frame"], "rtt"] = df.loc[i, "tcp.analysis.ack_rtt"]
    # map each rtt to seq
    print("max_seq", max_seq)
    print("maping each rtt to each seq...")
    seq_rtt = np.zeros(max_seq+1)
    for frame in tqdm(frame_seq_dict):
        for seq in frame_seq_dict[frame]:
            # 有時候會收到爛封包, seq超大
            try:
                if seq < max_seq:
                    seq_rtt[seq] = df.loc[frame, "rtt"]
            except:
                print("WTF", seq, frame)

                pass

    #############################################################################################################

    frame2_seq_dict = {}
    
    # map frame to eqch seq
    for i in tqdm(range(len(df2))):
        if df2.loc[i, "tcp.len"] > 0 and df2.loc[i, "tcp.len"] % length_packet == 0:
            dup_num = df2.loc[i, "tcp.len"] // length_packet
            frame_num = df2.loc[i, "frame.number"]
            frame2_seq_dict[frame_num] = []
            for j in range(dup_num):
                seq = int(df2.loc[i, "tcp.payload"][32+j*length_packet*2:48+j*length_packet*2], 16)
                frame2_seq_dict[frame_num].append(seq)
    
    # map rtt to each frame
    print("map rtt to each frame")
    # df.loc[df.loc[:, "tcp.analysis.acks_frame"], "rtt"] = df.loc[:, "tcp.analysis.ack_rtt"]

    for i in tqdm(range(len(df2))):
        if df2.loc[i, "tcp.analysis.acks_frame"]:
            df2.loc[df2.loc[i, "tcp.analysis.acks_frame"], "rtt"] = df2.loc[i, "tcp.analysis.ack_rtt"]
            # frame_rtt_dict[df.loc[i, "tcp.analysis.acks_frame"]] = df.loc[i, "tcp.analysis.ack_rtt"]

    # map each rtt to seq
    seq_rtt2 = np.zeros(max_seq+1)
    for frame in tqdm(frame2_seq_dict):
        for seq in frame2_seq_dict[frame]:
            # 有時候會收到爛封包, seq超大
            try:
                if seq <= max_seq:
                    seq_rtt2[seq] = df2.loc[frame, "rtt"]
            except:
                print("WTF", seq, frame)
                pass

    # print(seq_rtt)
    # print(seq_rtt2)
    # seq_rtt2[np.isnan(seq_rtt2) == 0]
    # seq_rtt[np.isnan(seq_rtt) == 0]
    merge_seq_rtt = np.vstack([seq_rtt, seq_rtt2]).min(axis=0)
    print(mean(merge_seq_rtt), mean(seq_rtt), mean(seq_rtt2))
    print(sum(merge_seq_rtt != 0), sum(seq_rtt != 0), sum(seq_rtt2 != 0))
    # plt.show()
    return seq_rtt, seq_rtt2



pcap_csv = r"C:\Users\USER\Desktop\data" + r"\DL1-10000.csv"
pcap_csv2 = r"C:\Users\USER\Desktop\data" + r"\DL2-10000.csv"

s1, s2 = rtt(pcap_csv=pcap_csv2, pcap_csv2=pcap_csv)


s = "00000000623a86410000000002d2477a000000000000000001c487aa5983bbd3bc80ded9a60f36d9056dfa3ff291e6da3a01c74f89aa1666435333af56d25d4b64c14489dca291ac3d8ed370a8731f082592de3d94fc30b12d38823d8c86560f01535f5a0fbcd0a9ce5321ef6a159e16ef7d521d21ab1bf56290956e7477317bffcdeebf6f18b5ed2c5c01dce17ec59e55d5242e7f6dd4445af1a7876521818ad333ba36d6b38928cf52a2f0cde7714a6287664a060ef2c4cf8e1b5566109409b4267b8d8abd2317cf1a0db125793a5e1e3e617fd82328d92d35ae390a196760b0650031f2bec5f93aef70a96eabc6a0d2cc6aa1c5c4e9489e42c7583a43d28787198f176295e03d57b0e6ca3f4b09da527c6d6fc3a03e96ebff775b1993a78eac53b841ad4d46f061b7dae2dcaa20870802d27d21f7f55790e3cf2beb7d7af3dab29ce438656788faf23d0bfacb4089b48a4db557aac6ced27a483b4cb4e8ddc4599abd16af2464654c00000000623a86410000000002d306f50000000000000001011a546d037735f381e3e8f031be79296cc7f80c3385f7aa1e2ca927fb7dd4372c84089e5b95387314869c276329a6d9e8833be27c06b22ea3370a59b1c26f0c5a6112f5a8e79b2eed59f8cc14ded310955a29a975b09858eecb22237a217d4701ca7c80229a816352128afddf79c94ddb6c196291c0d5a95b802a554ed1de5e69c05d09e63555393885d7430be3f97d0982bb173d403d532a7e94f5914861e168ec4668c766c52518b4063493c3bced88fcf554790695232044dc5bfd859d23aa4b03de3d5b716a61907114c20a49f6c0b724b595ab3c689518ac1899b0180fedc682aa1fe921be0601a23ce1e2e70cdb1f3bd1bc42f90e03a83f062344c51f3fa74c00a992ce6d0cb6667ddae23693960d0a6c366e0007bc6310f3f627f86f66359b7210d326bdf6c64ea742714eb54167772ed9b57db9d2d4358ef20a6869d7d2961e1461a889f81594ae764c9b32530400000000623a86410000000002d48d5e0000000000000002019148770d37bed0bba93f2814675b9bbf2454bf24f17d9508efc883fb2eeddc90c3d99388fb7ceaa5a7ff66d71cb951bdc0b301501ff21172234ddaf2fbca12e8b4823677f2aed09cda29aac3758a20b38ab54288e94e7906cef356da35c2b5dc90a75bf002f3f3f3f28b8e40104d56e51898666c67c3764adf56e641fbb78265cc2e1e6c1a7b11c2df917c71a7b23e36f5f7ebc7af9833549f238b6102f7d9ee311312930f1b566831f95b1aad464e2edbb977c7feb497d1d663ba1778371934abe8e9d2dd30139776a218ac59db770417534632c809c9e82b2a2322580a54a56b2de2551a2b2c15d575ff0f9dda8dc8f566d38b0c2176e2e543703874dc8f1df006599de041e10322d21026776ee622422c1daa70dd79345c994ae85554fc4314babd0d059d4d0d350fc25a2329befcf0403e76162220761987bd71b5e3d01e748adf30a557ed7beefbe083955cb85dab00000000623a86410000000002d529bd0000000000000003013d246771963e71a975b0e2f6ec431812006e1cdda7bcd3b963181dfb26f9f790230a62f6bf5749e22a35b3ca48d789ab8521079947e099f2c2c872889b63858e9663c41ceecddacacb47507d2f67b709a8824ec38bce88e06f1e5b26e304efa99a16e95719e36d76a313e117a124e44bc88edd6efe36a82d2a677eab4fe5aa0ed9e71564d249aeb5e60eed55d05495bf781ace8b8c4217d65943d36b63892f5d1aa461db8aa6a184564d1a8d9f3f0f204f83f62967ab91dac015b3a0693a34d3c8916c357135d115a87ecca1b19d72bfcfcc2f2f2e1a38c2fab73539c4fe6910f702fdb8e36e4b9a6f01d3fe76b5b88ca5e7210bea249702a9a4cbd35a67699418680fe173f489da6e04482e92660ee33c171ebbc754dfcaa3b88943b5b0f8cf43f425b89e0892eddd74921a55e10949e9c32f17736b0cd5b0137a6bf50eb9d5dbe6e4867e5e6d83a3fd57d36069f1ef72"

