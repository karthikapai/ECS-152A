# client
from socket import *
import os
serverName = input('enter your server address: ')
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
print('Server address is: ', serverName)
print('Socket', clientSocket.fileno(), 'opened to server', serverName, ':', serverPort)

while True:
	firstName = input('Please enter your message: ')
	if (firstName == 'exit'):
		clientSocket.close()
		break
	clientSocket.send(str.encode(firstName))
	response = clientSocket.recv(1024)
	print('Server says:', bytes.decode(response))

