import socket
import threading
import queue
import pickle
import infoObjects

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
server =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

def recieve():
    while True:
            print("LISTENING")
            message, adr = server.recvfrom(1024)
            messageObject = pickle.loads(message)
            messages.put((messageObject,  adr))
            handleClientInfo()


def setPlayerInfo(index, nickname, protocol):
    playerObject = infoObjects.infoPlayerObject((index*200, index*100), GROUP, nickname, protocol) #here the sprite group string will be used as the value for the sprite group, you just have to destringify it
    players.append(playerObject)

def setObjects(): #NEEDS TO BE UPDATED WHEN WE CHANGE UP THE MAP A BIT
    barrelObject = infoObjects.infoObjectObject(BARREL_POSITION, GROUP)
    objects.append(barrelObject)

def setWeapons():
    index = 0
    for i in range(1, 5):
        weaponObject = infoObjects.infoWeaponObject(300 + index, GROUP, i)
        weapons.append(weaponObject)
        index += 200

def handleClientInfo():
    while not messages.empty():
        messageObject, adr = messages.get()
        print(messageObject)
        if messageObject.protocol == "NAME":
            print("GOT THE HANDSHAKE MESSAGE") ##DEBUGGING
            nickname = messageObject.nickname 
            usernames.append(nickname)
            clients.append(adr)
            index = clients.index(adr)
            setPlayerInfo(index, nickname, "NEW_PLAYER")   
            print(f'USERNAMES: {usernames}') 
        if messageObject.protocol == "CLIENT_INFO": #THIS WILL GIVE YOU A GOOD IDEA HOW THE BIG INFO OBJECT NEEDS TO LOOK
            index = usernames.index(messageObject.player.nickname) 
            players[index].pos = messageObject.player.pos
            for bullet in messageObject.bulletList:
                bullets.append(bullet) #needs to be cleared after every time we send info to clients for the bullets
            for weapon in messageObject.weaponList:
                for oldWeapon in weapons:   #MIGHT NEED TO BE CHANGED IF PERFORMANCE IS FUCKED BUT I CANT THINK OF ANYTHING BETTER RN
                    if oldWeapon.id == weapon.id:
                        oldWeapon.pos = weapon.pos
        if messageObject.protocol == "DISCONNECT":
            nicknameIndex = usernames.index(messageObject.nickname)
            players[nicknameIndex].protocol = "DISCONNECT"
        else:
            pass

def broadcast():
    while True:
            for player in players:
                if player.protocol == "NEW_PLAYER":
                    index = players.index(player)
                    serverInfo = infoObjects.generalServerInfo("HANDSHAKE", players, objects, weapons, bullets) ##HERE I REMOVED THE player.nickname PARAMETER BETWEEN PLAYERS AND MAP
                    serverInfoToBeSend = pickle.dumps(serverInfo)
                    print(serverInfoToBeSend)
                    print(clients[index])
                    server.sendto(serverInfoToBeSend, clients[index])
                if player.protocol == "DISCONNECT":
                    disconnectObject = pickle.dumps(infoObjects.disconnectionObject(player.nickname, player.protocol))
                    server.sendall(disconnectObject)
                else:
                    player.protocol = "UPDATE_STATE"
                    playerObject = pickle.dumps(player)
                    for client in clients:
                        server.sendto(playerObject, client)
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