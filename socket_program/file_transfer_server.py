from fileinput import filename
import socket
from threading import Thread
import os

TCP_IP = '192.168.1.248'
TCP_PORT = 3280
BUFFER_SIZE = 4096


class ClientThread(Thread):

    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print(" New thread started for "+ip+":"+str(port))

    def run(self):
        devicename = self.sock.recv(BUFFER_SIZE).decode()
        filename = self.sock.recv(BUFFER_SIZE).decode()
        print("-"*30)
        if not os.path.exists(devicename):
            os.system("mkdir %s"%(devicename))
        file_exists = os.path.exists(os.path.join(".", devicename, filename))

        print("filename:", filename)
        print("device:", devicename)
        # print(os.path.join(".", devicename, filename))
        if file_exists:
            self.sock.sendall(b"NO")
            return
        else:
            self.sock.sendall(b"OK")
        with open(os.path.join(".", devicename, filename), 'wb') as f:
            print('file opened')
            while True:
                #print('receiving data...')
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    f.close()
                    print('file close()')
                    break
                # write data to a file
                f.write(data)

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
threads = []

while True:
    tcpsock.listen(10)
    print("Waiting for incoming connections...")
    (conn, (ip, port)) = tcpsock.accept()
    print('Got connection from ', (ip, port))
    newthread = ClientThread(ip, port, conn)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
