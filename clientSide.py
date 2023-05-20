import socket
import pickle
import threading

class ClientSide():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = "127.0.0.1"
        self.port = 53000
        self.address = (self.server, self.port)
    
    def receiveHandshake(self):
        self.client.bind(self.address)

        while True:
            data, addr = self.client.recvfrom(1024)
    
    def sendHandshake(self):
        nickname = 
        






