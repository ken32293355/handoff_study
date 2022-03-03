import os
import sys


print(len(sys.argv))

assert(len(sys.argv) == 2)

if sys.argv[1] == "START":
    for i in range(10):
        os.system("python3 packet_UD_server.py -p %d&"%(3230+i))
elif sys.argv[1] == "STOP":
    os.system("./kill_socket.py")


