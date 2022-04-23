# Echo server program
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5431              # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.setsockopt(socket.SOL_TCP, 42, 1)
    # s.setsockopt(6, 42, 1)
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)