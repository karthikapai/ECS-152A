# simple (non-concurrent) TCP server example
from socket import *
serverPort = 12000
listeningSocket = socket(AF_INET, SOCK_STREAM)
listeningSocket.bind(('', serverPort))
listeningSocket.listen(1)
print('Server ready, socket', listeningSocket.fileno(), 'listening on localhost :', serverPort)
connectionSocket, addr = listeningSocket.accept()
while True:
    firstName = connectionSocket.recv(1024)
    if (firstName == 'exit'):
        print('Closing socket', connectionSocket.fileno())
        connectionSocket.close()
        continue
    print('Got connection on socket', connectionSocket.fileno(), 'from', addr[0], ':', addr[1])
    print(addr[0], ': ', bytes.decode(firstName))
    connectionSocket.send(str.encode(bytes.decode(firstName)))

