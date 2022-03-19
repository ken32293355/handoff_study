import subprocess
import re
import datetime as dt
port = 3233
proc = subprocess.Popen(["ss -ai dst :%d"%(port)], stdout=subprocess.PIPE, shell=True)
print(dt.datetime.now())
# while True:
#     line = proc.stdout.readline().decode().strip()
#     if not line:
#         break
#     print("-"*10)
#     print(line)
#     print(",".join(re.split("[: \n\t]", line)))
#     print("-"*10)
