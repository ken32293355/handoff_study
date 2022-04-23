import os
import sys

port_list = [3251, 3257, 3259, 3239, 3263, 3255, 3247, 3245, 3241, 3261]

for p in port_list:
	os.system("sudo python3 tcp_UD_server.py -p %d&"%(p))


