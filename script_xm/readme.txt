----------------------------------------------------------------------
一、取得 iperf3 & tcpdump
*** 若 /sdcard/script 資料夾中已存在這兩個檔案，且執行時一切正常，可跳過此步驟

(1) 下載 Network Signal Guru ，開啟應用並給予各項權限（包含超級使用者權限）
(2) 到 /data/data/com.qtrun.QuickTest/files 將 iperf3 和 tcpdump 複製到 /sdcard/script

$ su
$ cd /data
$ find . -name *iperf3*
$ cp ./data/com.qtrun.QuickTest/files/iperf3 /sdcard/script
$ find . -name *tcpdump*
$ cp ./data/com.qtrun.QuickTest/files/tcpdump /sdcard/script

[Problem #1]
$ cp ./data/com.qtrun.QuickTest/files/iperf3 /sdcard/script
cp: /sdcard/script/iperf3: No such file or directory

=> 打開 Network Signal Guru ，允許各項權限，再次輸入指令即可解決

----------------------------------------------------------------------
二、connect.sh & disconnect.sh

(1) 透過 Sublime Text 打開 /sdcard/script 資料夾中的 connect.sh ，將 [uplink port] & [downlink port] 改成手機背後指定的 port number ，奇數為 uplink ，偶數為 downlink

e.g.,

   /sbin/iperf3 -c 140.112.20.183 -p [uplink port] -u -V -t 10800 -l 250 -b 200k&
=> /sbin/iperf3 -c 140.112.20.183 -p 3231 -u -V -t 10800 -l 250 -b 200k&

(2) 若 /sdcard 資料夾中沒有名為 dataset 的資料夾，則自己創建一個

$ cd /sdcard
$ mkdir dataset

----------------------------------------------------------------------
三、將 script 移動到 /sbin 資料夾內，為其添加可執行權限
*** 每當手機重新開機時，就要再進行此步驟

$ su
$ cd /sbin
$ cp /sdcard/script/* .
$ chmod +x *
chmod: chmod 'setlockstate' to 100751: Read-only file system <= 可忽視這則訊息

----------------------------------------------------------------------
四、執行

(1) 打開 server 端的監聽
(2) 執行 disconnect.sh 確保手機背景沒有未關閉的 iperf3 和 tcpdump 的程序

$ su
$ cd /sbin
$ ./disconnect.sh

(3) 執行 connect.sh 開始實驗（執行 iperf3 並寫入檔案）

$ ./connect.sh

(4) 開啟第二個命令視窗，執行 disconnect.sh 結束實驗並存檔

$ su
$ cd /sbin
$ ./disconnect.sh

(5) 關閉 server 端的監聽

[Problem #2]
若透過 Termius 執行時，不斷出現以下錯誤提示
iperf3: error - unable to create a new stream: No such file or directory

=> 改用 Termux 有可能解決這問題（Termius 似乎看不到某些檔案）
Termux 可在下拉選單，點選 "Acquire wakelock" ，確保在背景執行不休眠

