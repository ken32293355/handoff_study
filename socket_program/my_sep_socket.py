import os
import sys


for i in range(0, 8, 2):
	c = "python3 seperate_UD2_server.py -p1 %d -p2 %d&"%(3230+i, 3230+i+1)
	os.system(c)


