import os
import sys


for i in range(8):
	os.system("python3 packet_UD_server.py -p %d&"%(3230+i))


