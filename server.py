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
adresses = []
map = "map1Test.tmx"
GROUP = "spriteGroup"
BARREL_POSITION = (200, 200) #NEEDS TO BE UPDATED WHEN WE CHANGE UP THE MAP A BIT
messages = queue.Queue()
sendingQueue = queue.Queue()
server =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("192.168.0.108", 9998))
idlePosition = pygame.math.Vector2(0, 0)

#server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
#server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)

def recieve():
    while True:
       # try:
                message, adr = server.recvfrom(2048)
                messageObject = pickle.loads(message)
                messages.put((messageObject,  adr))
                handleClientInfo()
       # except:
            #print("Listening...")



def setPlayerInfo(index, nickname, protocol):
    playerObject = infoObjects.infoPlayerObject((index*200, index*100), GROUP, nickname, protocol, idlePosition, 0) #here the sprite group string will be used as the value for the sprite group, you just have to destringify it
    players.append(playerObject)

def setObjects(): #NEEDS TO BE UPDATED WHEN WE CHANGE UP THE MAP A BIT
    barrelObject = infoObjects.infoObjectObject(BARREL_POSITION, GROUP)
    objects.append(barrelObject)

def setWeapons():
    index = 0
    for i in range(1, 5):
        weaponObject = infoObjects.infoWeaponObject(300 + index,300 + index, GROUP,i , "", 0)
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
            #print(f'INDEX: {index}')
            setPlayerInfo(index, nickname, "NEW_PLAYER")   
        if messageObject.protocol == "CLIENT_INFO": #THIS WILL GIVE YOU A GOOD IDEA HOW THE BIG INFO OBJECT NEEDS TO LOOK
            #print(messageObject, messageObject.nickname, messageObject.protocol)
            index = usernames.index(messageObject.nickname) 
            players[index].positionVector = messageObject.positionVector
            players[index].pos = messageObject.pos
            players[index].angle_pointing = messageObject.angle_pointing

            for weapon in weapons:
                if weapon.id == messageObject.weaponOwnedId:
                    weapon.owner = messageObject.nickname

            #print(messageObject.bulletsShot)

            #for bullet in messageObject.bulletsShot:
             #   print("RECEIVED BULLET")
              ##  bullets.append(bullet)
                #if not len(messageObject.bulletsShot) == 0:
                 #   print(f'BULLETS APPENDED WITH:{bullet} ')
            
             #needs to be cleared after every time we send info to clients for the bullets
        if messageObject.protocol == "NEW_BULLET":
            print(f'RECEIVED NEW BULLET: {messageObject}')
            bullets.append(messageObject)

        if messageObject.protocol == "DISCONNECT":
            print("GOT THE MESSAGe")
            nicknameIndex = usernames.index(messageObject.nickname)
            players[nicknameIndex].protocol = "DISCONNECT"
            players.remove(players[nicknameIndex])

        if messageObject.protocol == "BACK_PING":
            if adr in clients:
                print("all good")

            else:
                client_index = usernames.index(messageObject.nickname)
                clients.remove()
                del players[client_index]
                del usernames[client_index]
                print("client removed due to inactivity")
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
                    #print(bullets)
                    serverInfo = pickle.dumps(serverInfo)
                    for client in clients:
                        server.sendto(serverInfo, client)
                    bullets.clear()

def ping():
     threading.Timer(1, ping).start()
     if len(players) > 0:
        print("entered function")
        for client in clients:
            pingObj = infoObjects.pingObject("PING")
            server.sendto(pickle.dumps(pingObj), client)
            print("pign sent")

        



def main ():
    setObjects()
    setWeapons()
    t1 = threading.Thread(target = recieve)
    t2 = threading.Thread(target = broadcast)
    t1.start()
    t2.start()
    ping()

if __name__ == "__main__":
    main()