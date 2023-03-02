# client application (for testing)
import socket
import config

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((config.HOST, config.PORT))
    s.sendall(b'get_currency@e')
    data = s.recv(1024)
print(data.decode('utf-8'))
