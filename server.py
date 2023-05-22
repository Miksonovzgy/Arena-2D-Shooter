import socket
import threading
import queue
import pickle
import infoObjects
import pygame

clients = []
usernames = []
weapons = []
players = []
bullets = []
objects = []
map = "map1Test.tmx"
GROUP = "spriteGroup"
BARREL_POSITION = (200, 200) #NEEDS TO BE UPDATED WHEN WE CHANGE UP THE MAP A BIT
messages = queue.Queue()
sendingQueue = queue.Queue()
server =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))
idlePosition = pygame.math.Vector2(0, 0)

server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

def recieve():
    while True:
            message, adr = server.recvfrom(1024)
            messageObject = pickle.loads(message)
            messages.put((messageObject,  adr))
            handleClientInfo()


def setPlayerInfo(index, nickname, protocol):
    playerObject = infoObjects.infoPlayerObject((index*200, index*100), GROUP, nickname, protocol, idlePosition) #here the sprite group string will be used as the value for the sprite group, you just have to destringify it
    players.append(playerObject)

def setObjects(): #NEEDS TO BE UPDATED WHEN WE CHANGE UP THE MAP A BIT
    barrelObject = infoObjects.infoObjectObject(BARREL_POSITION, GROUP)
    objects.append(barrelObject)

def setWeapons():
    index = 0
    for i in range(1, 5):
        weaponObject = infoObjects.infoWeaponObject(300 + index,300 + index, GROUP, i, "")
        weapons.append(weaponObject)
        index += 200

def handleClientInfo():
    while not messages.empty():
        messageObject, adr = messages.get()
        if messageObject.protocol == "NAME":
            nickname = messageObject.nickname 
            usernames.append(nickname)
            clients.append(adr)
            index = clients.index(adr)
            print(f'INDEX: {index}')
            setPlayerInfo(index, nickname, "NEW_PLAYER")   
        if messageObject.protocol == "CLIENT_INFO": #THIS WILL GIVE YOU A GOOD IDEA HOW THE BIG INFO OBJECT NEEDS TO LOOK
            #print(messageObject, messageObject.nickname, messageObject.protocol)
            index = usernames.index(messageObject.nickname) 
            players[index].positionVector = messageObject.positionVector
            players[index].pos = messageObject.pos
            for bullet in messageObject.bulletsShot:
                bullets.append(bullet)
             #needs to be cleared after every time we send info to clients for the bullets

        if messageObject.protocol == "DISCONNECT":
            nicknameIndex = usernames.index(messageObject.nickname)
            players[nicknameIndex].protocol = "DISCONNECT"
        else:
            pass

def broadcast():
    while True:
            for player in players:
                if player.protocol == "NEW_PLAYER":
                    player.protocol = "UPDATE_STATE"
                if player.protocol == "DISCONNECT":
                    #print("molqqqq>.") #means "whaaaaaaat?!" in bulgarian :)
                    disconnectObject = pickle.dumps(infoObjects.disconnectionObject(player.nickname, player.protocol))
                    server.sendall(disconnectObject)
                else:
                    #playerObject = pickle.dumps(player)
                    serverInfo = infoObjects.generalServerInfo("UPDATE_STATE", players, objects, weapons, bullets) ##HERE I REMOVED THE player.nickname PARAMETER BETWEEN PLAYERS AND MAP
                    serverInfo = pickle.dumps(serverInfo)
                    for client in clients:
                        server.sendto(serverInfo, client)
            bullets.clear()

def main ():
    setObjects()
    setWeapons()
    t1 = threading.Thread(target = recieve)
    t2 = threading.Thread(target = broadcast)
    t1.start()
    t2.start()

if __name__ == "__main__":
    main()