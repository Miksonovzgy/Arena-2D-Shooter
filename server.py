import socket
import threading
import queue
import pickle
import infoObjects
import pygame
import math


spriteGroup = pygame.sprite.Group()

clients = []
usernames = []
weapons = []
players = []
bulletsObjects = []
bulletsInfo = []
objects = []
map = "map1Test.tmx"
GROUP = "spriteGroup"
BARREL_POSITION = (200, 200) #NEEDS TO BE UPDATED WHEN WE CHANGE UP THE MAP A BIT
messages = queue.Queue()
sendingQueue = queue.Queue()
server =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("192.168.0.108", 9999))
idlePosition = pygame.math.Vector2(0, 0)

server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)

class BulletOnServer(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, group, shooter, id, angle = 0):
        super().__init__(group)
        self.position = pygame.math.Vector2()
        self.position.x = pos_x
        self.position.y = pos_y
        self.rect = pygame.Rect(pos_x, pos_y, 32/3, 80/3)

            
        self.bullet_speed = 10
        self.shooter = shooter
        self.id = id

        self.angle = angle
        self.dx = math.cos(self.angle) * self.bullet_speed
        self.dy = math.sin(self.angle) * self.bullet_speed




    def move(self):
        self.position.x += self.dx
        self.position.y += self.dy
        #print(f'BULLETS ARE MOVING BY: {self.position.x, self.position.y}')
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        if self.checkForCollisionWithBorder():
            bulletsObjects.remove(self)
            destroyBullet = infoObjects.destroyBulletInfoObject("DESTROY_BULLET", self.id)
            destroyBulletObject = pickle.dumps(destroyBullet)
            for client in clients:
                server.sendto(destroyBulletObject, client)


    
    def checkForCollisionWithBorder(self):
        if (self.rect.x >= 31 * 128) or (self.rect.x <= 0) or (self.rect.y >= 31 * 120) or (self.rect.y <= 0):
            return True





def recieve():
    while True:
        #try:
                message, adr = server.recvfrom(4096)
                messageObject = pickle.loads(message)
                messages.put((messageObject,  adr))
                handleClientInfo()
        #except:
            #print("oopsi")




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
            print(f'SETTING {nickname}')
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


        if messageObject.protocol == 'NEW_BULLET':
            if len(bulletsObjects) != 0:
                for presentBullet in bulletsObjects:
                    if presentBullet.id != messageObject.id:
                        print("APPENDED")  
                        bulletsObjects.append(BulletOnServer(messageObject.posX, messageObject.posY, spriteGroup,messageObject.shooter, messageObject.id, messageObject.angle))
            else:
                bulletsObjects.append(BulletOnServer(messageObject.posX, messageObject.posY, spriteGroup, messageObject.shooter, messageObject.id, messageObject.angle))
            
            messageObject.protocol = "NEW_BULLET_SERVERSIDE"
            for client in clients:
                server.sendto(pickle.dumps(messageObject), client)
                
             #needs to be cleared after every time we send info to clients for the bullets

        #if messageObject.protocol == "DISCONNECT":
          #  print("GOT THE MESSAGe")
          #  nicknameIndex = usernames.index(messageObject.nickname)
          #  players[nicknameIndex].protocol = "DISCONNECT"
          #  del players[nicknameIndex]
           # del nickname[nicknameIndex]
            #del clients[nicknameIndex]


        if messageObject.protocol == "BACK_PING":
            if adr in clients:
                print("all good")

            else:
                client_index = usernames.index(messageObject.nickname)
                del clients[client_index]
                del players[client_index]
                del usernames[client_index]
                print("client removed due to inactivity")
        else:
            pass

def broadcast():
    while True:
        if len(bulletsObjects) != 0:
            for bullet in bulletsObjects:
                bullet.move()
        for player in players:
            if player.protocol == "NEW_PLAYER":
                player.protocol = "UPDATE_STATE"
            if player.protocol == "DISCONNECT":
                #print("molqqqq>.") #means "whaaaaaaat?!" in bulgarian :)
                disconnectObject = pickle.dumps(infoObjects.disconnectionObject(player.nickname, player.protocol))
                server.sendall(disconnectObject)
            else:
                #playerObject = pickle.dumps(player)
                #for bullet in bulletsObjects:
                 #   newBullet = infoObjects.infoBulletsObject(bullet.rect.x, bullet.rect.y, bullet.shooter, bullet.id, bullet.angle)
                    #bulletIndex = bulletsObjects.index(bullet)
                  #  bulletsInfo.append(newBullet)


                serverInfo = infoObjects.generalServerInfo("UPDATE_STATE", players, objects, weapons, bulletsInfo) ##HERE I REMOVED THE player.nickname PARAMETER BETWEEN PLAYERS AND MAP
    
                #if len(bulletsInfo) != 0:
                    #print(f'BULLETS AFTER: {bulletsInfo}')
                serverInfo = pickle.dumps(serverInfo)
                for client in clients:
                    server.sendto(serverInfo, client)

def handlingTheBullets():
    while True:
        if len(bulletsObjects) != 0:
            for bullet in bulletsObjects:
                bullet.move()
            bulletsObjects.clear()
            bulletsInfo.clear()
        else:
            pass


def ping():
     threading.Timer(4, ping).start()
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
    #t3 = threading.Thread(target = handlingTheBullets)
    t1.start()
    t2.start()
    #t3.start()
    #ping()

if __name__ == "__main__":
    main()