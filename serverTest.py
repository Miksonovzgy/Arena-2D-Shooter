import socket
import threading
import queue

messages = queue.Queue()
clients = []

server =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

def recieve():
    while True:
        try:
            message, adr = server.recvfrom(1024)
            messages.put((message, adr))
        except:
            pass

def broadcast():
    while True:
        while not messages.empty():
            message, adr = messages.get()
            print(message.decode())
            if adr not in clients:
                clients.append(adr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        print(message)
                        name = message.decode()[message.decode().index(":")+1:]
                        server.sendto(f"{name}, joined", client)
                    else:
                        print(message)
                        server.sendto(message, client)
                except:
                    clients.remove(client)

t1 = threading.Thread(target = recieve)
t2 = threading.Thread(target = broadcast)

t1.start()
t2.start()
    
                