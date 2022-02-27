#!/usr/bin/env python3

import os
os.system("pkill tcpdump") 
os.system("kill -9 $(ps -A | grep python | awk '{print $1}')") 
