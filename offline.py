import pygame
import os
import sys
import ctypes
import time
from pytmx.util_pygame import load_pygame
import random
import math
import infoObjects
import pickle
import socket
import threading
import queue
import os


pygame.init()
OBJECTS = []
PLAYER_NICKNAMES = []
FPS = 60
SCREEN_INFO = pygame.display.Info()
WIDTH,HEIGHT = 1280, 720
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
BG = pygame.image.load("sprites\sci-fiPlatform\png\Tiles\Acid (2).jpg")
BG = pygame.transform.scale(BG,(WIDTH, HEIGHT))
ANIMATION_SPEED = 3
PLAYER_SIZE= [100, 100]
BARREL_SIZE = (177/3, 238/3)
WEAPON_SIZE = (412/7,166/7)
BULLET_SIZE = (32/3, 80/3)
TILE_SIZE = [128, 120]
BULLETS_ON_MAP = []
MY_BULLETS_ON_MAP = []
MY_BULLETS_ON_MAP_INFO = []
PLAYERS_ON_MAP = []
WEAPONS_ON_MAP = []
MAP_INDEX = 1
CAN_SEND = False


updateMessages = queue.Queue()
sendingQueue = queue.Queue()

NICKNAME = input("Input Nickname: ")

TMX_DATA = load_pygame(f'map{MAP_INDEX}Test.tmx') #IMPORTANT: dont forget to change map collisions after chaning the map

class CameraGroup(pygame.sprite.Group): 
    def __init__(self):                 #STRONGLY RECOMMEND: SEE HOW I MAKE IMAGES WITH THIS AND MAKE THE OTHER OBJECTS THE SAME WAY
        super().__init__()
        self.displayScreen = pygame.display.get_surface()
        self.cameraX = self.displayScreen.get_size()[0]/2
        self.cameraY = self.displayScreen.get_size()[1]/2
        self.offset = pygame.math.Vector2() #this is for centering
        self.cameraRect = pygame.Rect(200, 100, self.displayScreen.get_size()[0] - (200 + 200), self.displayScreen.get_size()[1] - (100 + 100)) #TO DO: replace with constants

    def cameraDraw(self): #this is the important stuff, im essentially modyfing the draw function here

        player = findPlayer()
        if hasattr(player, 'rect'):
            self.offset.x = player.rect.centerx - self.cameraX
            self.offset.y = player.rect.centery - self.cameraY #this is for centering
        #for sprite in self.sprites(): #draws every sprite (which for now is pistol, barrel and player)
           #print("a")
           #print(sprite)
        for sprite in self.sprites(): #draws every sprite (which for now is pistol, barrel and player)
            if hasattr(sprite, 'rect'):
                offsetPosition = sprite.rect.topleft - self.offset
                self.displayScreen.blit(sprite.image, offsetPosition)

spriteGroup = CameraGroup() 

class ClientSide():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = "localhost"
        self.clientPort = random.randint(8000, 9000)
        self.port = 9998
        self.address = (self.server, self.port)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)
        self.sending_state = False
    
    def sendHandshake(self, nickname):
        print(nickname)
        newPlayerInfo = infoObjects.disconnectionObject(nickname, "NAME")
        newPlayerObject = pickle.dumps(newPlayerInfo)
        self.client.sendto(newPlayerObject, self.address)
    
    def sendDisconnection(self, nickname):
        disconnectionInfo = infoObjects.disconnectionObject(nickname, "DISCONNECTION")
        disconnectionInfoObject = pickle.dumps(disconnectionInfo)
        print("DISCONNECTION SENT")
        self.client.sendto(disconnectionInfoObject, self.address)
    

    def handleIncomingServerInfoUpdate(self):
        while True:
            message, _ = self.client.recvfrom(4096)
            infoFromServer = pickle.loads(message)
            updateMessages.put(infoFromServer)

            if not updateMessages.empty():
                updateInfo = updateMessages.get()

                if updateInfo.protocol == "PING":
                    backPingObj = infoObjects.pingObject("BACK_PING", NICKNAME)
                    #print("sending backping")
                    backPingObj = pickle.dumps(backPingObj)
                    self.client.sendto(backPingObj, self.address)

                if updateInfo.protocol == "UPDATE_STATE":
                    for player in updateInfo.playerList:
                        if player.nickname == NICKNAME:
                            if player.nickname not in PLAYER_NICKNAMES:
                                player = Player(player.pos, spriteGroup, player.nickname, True)
                        else:
                            if player.nickname not in PLAYER_NICKNAMES:
                                player = Player(player.pos, spriteGroup, player.nickname, False)
                                #print("drew players")
                            else:
                                index = PLAYER_NICKNAMES.index(player.nickname)
                                PLAYERS_ON_MAP[index].position = player.positionVector
                                PLAYERS_ON_MAP[index].rect.center = player.pos ##ADDED
                                PLAYERS_ON_MAP[index].angle_pointing = player.angle_pointing
                    
                    if len(WEAPONS_ON_MAP) == 4:
                        for weapon in updateInfo.weaponList:
                            index = updateInfo.weaponList.index(weapon)
                            WEAPONS_ON_MAP[index].posX = weapon.posX
                            WEAPONS_ON_MAP[index].posY = weapon.posY
                            WEAPONS_ON_MAP[index].id = weapon.id
                            WEAPONS_ON_MAP[index].owner = weapon.owner

                            for player in PLAYERS_ON_MAP:
                                if player.nickname == weapon.owner:
                                    WEAPONS_ON_MAP[index].angle_to_rotate = player.angle_pointing
                                    #print(f'WEAPON: {WEAPONS_ON_MAP[index].owner} ANGLE TO ROTATE IS: {WEAPONS_ON_MAP[index].angle_to_rotate}')
    
                    else:
                        for weapon in updateInfo.weaponList:
                            weapon = Weapon(weapon.posX, weapon.posY, spriteGroup, weapon.id, weapon.owner)
                            #if weapon.id == weapon.id:
                               # weapon.owner = weapon.owner
                    #for barrel in updateInfo.objectList:
                        #if len(OBJECTS) == 0:
                          #  barrel = ObjectBarrel(barrel.pos, spriteGroup)
                
                if updateInfo.protocol == "NEW_BULLET_SERVERSIDE":
                    #print("GOT TO BULLET MODULE")
                    ids = []
                    for currentBullet in BULLETS_ON_MAP:
                        ids.append(currentBullet.id)
                    if updateInfo.id not in ids:
                        #print("APPENDED")
                        BULLETS_ON_MAP.append(Bullet(updateInfo.posX, updateInfo.posY, spriteGroup, updateInfo.shooter, updateInfo.id, updateInfo.angle))
                        #print(BULLETS_ON_MAP)
                
                if updateInfo.protocol == "DESTROY_BULLET":
                    for bullet in BULLETS_ON_MAP:
                        if bullet.id == updateInfo.id:
                            BULLETS_ON_MAP.remove(bullet)
                            spriteGroup.remove(bullet)


                if updateInfo.protocol == "DISCONNECT":
                    index = PLAYER_NICKNAMES.index(updateInfo.nickname)
                    del PLAYERS_ON_MAP[index]
                          
               
    def sendInfoToServer(self):
        while True:
            ourPlayer = findPlayer()
            if self.sending_state:
                    for weapon in WEAPONS_ON_MAP:
                        if weapon.owner == NICKNAME:
                            bulletID = random.randint(1, 10000)
                            bullet_info = infoObjects.infoBulletsObject(weapon.rect.x, weapon.rect.y, ourPlayer.nickname, bulletID, ourPlayer.angle_pointing, "NEW_BULLET")
                            self.client.sendto(pickle.dumps(bullet_info), client.address)
                            self.sending_state = False
                            #print("SENT")

            if hasattr(ourPlayer, 'position'):
                if hasattr (ourPlayer, 'nickname'):
                    #print(f'OUR PLAYER POINTING: {ourPlayer.angle_pointing}')
                    bulletsShot = []

                    #if len(bulletsShot) != 0:
                        #print(f"SENDING {bulletsShot}")
                    ourPlayerInfo = infoObjects.generalClientInfo("CLIENT_INFO", ourPlayer.position, ourPlayer.rect.center, ourPlayer.nickname, bulletsShot, ourPlayer.weaponId, ourPlayer.angle_pointing) ##ADDED


                    #if(len(bulletsShot)!= 0):
                        #print(f'BULLETS ARRAY: {ourPlayerInfo.bulletsShot}')

                    ourPlayerInfoObject = pickle.dumps(ourPlayerInfo)
                    self.client.sendto(ourPlayerInfoObject, self.address)

                    

client = ClientSide()

class Tile(pygame.sprite.Sprite): #WATCH TUTORIAL
    def __init__(self, pos, surf: pygame.Surface, group): #,group
        super().__init__(group) #group
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
def mapDraw(): #WATCH TUTORIAL      

    for tiles in TMX_DATA.layers:
        if hasattr(tiles, 'data'):
            for x,y,surf in tiles.tiles():
                pos = (x * TILE_SIZE[0], y * TILE_SIZE[1])
                Tile(pos = pos, surf = surf, group = spriteGroup)#tileSpriteGroup)
mapDraw()    

class Background(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load("sprites\sci-fiPlatform\png\Tiles\Acid (2).png")
        self.image = pygame.transform.scale(BG,(WIDTH, HEIGHT))
        self.rect = self.image.get_rect()

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, nickname, isPlayable):
        super().__init__(group)
        self.group = group
        self.imagesAnimationUp = []
        self.imagesAnimationDown = []
        self.imagesAnimationLeft = []
        self.imagesAnimationRight = []
        self.imageIndex = 0
        self.animationCooldown = 0
        self.position = pygame.math.Vector2() 
        self.speed = 50
        self.weapon = False
        self.weaponId = 0
        self.ammo = 500
        self.health = 3
        self.nickname = nickname
        self.isPlayable = isPlayable
        self.image = pygame.image.load(f'sprites/player1.png')
        self.rect = self.image.get_rect(topleft = pos)
        self.rect.width = self.rect.width - 35
        PLAYERS_ON_MAP.append(self)
        PLAYER_NICKNAMES.append(nickname)
        self.angle_pointing = 0

        for i in range(1, 4):
            image = pygame.image.load(f'sprites/player{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            self.imagesAnimationUp.append(image)

        for i in range(1, 4):
            image = pygame.image.load(f'sprites\playerDown{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            self.imagesAnimationDown.append(image)

        for i in range(1, 4):
            image = pygame.image.load(f'sprites\playerLeft{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            self.imagesAnimationLeft.append(image)
        
        for i in range(1, 4):
            image = pygame.image.load(f'sprites\playerRight{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            self.imagesAnimationRight.append(image)
        self.image = self.imagesAnimationUp[self.imageIndex]
    
    def playerInput(self, x = 0, y = 0): #new way of calculatng movement and next position, this implementation might be usefull for the UDP 
        keys = pygame.key.get_pressed()
        if self.isPlayable:
            if keys[pygame.K_w]:  #from the key presses i store only what the position of the object is suppossed to be
                self.position.y = -1
            elif keys[pygame.K_s]:
                self.position.y = +1
            else:
                self.position.y = 0

            if keys[pygame.K_d]:
                self.position.x = +1
            elif keys[pygame.K_a]:
                self.position.x = -1
            else:
                self.position.x = 0

    def animations(self): #made a function to handle animations cuz why not
        if self.position.y == -1:
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                   self.imageIndex = 0
                self.image = self.imagesAnimationUp[self.imageIndex]
                self.animationCooldown = 0
        elif self.position.y == 1:
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationDown[self.imageIndex]
                self.animationCooldown = 0
        elif self.position.x == -1:
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationLeft[self.imageIndex]
                self.animationCooldown = 0
        elif self.position.x == 1:
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationRight[self.imageIndex]
                self.animationCooldown = 0

    def updatePlayer(self, events, spriteGroup):

        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x -  WIDTH/2, -(mouse_y - HEIGHT/2)

        self.angle_pointing = math.atan2(-dy, dx) ##IMPORTANT CHANGE / NOW WE STORE THE ANGLE AT WHICH EACH PLAYER IS POINTING

        #self.checkIfShooting(events, spriteGroup)
        self.playerInput()
        self.animations()
        #self.checkForHits()
        self.checkForHealth()
        self.healthDisplay()
        self.nicknameDisplay()
        self.ammoDisplay()
        

        speed = self.speed
        position = self.position

        if (self.rect.x >= 31 * TILE_SIZE[0] and self.position.x == 1) or (self.rect.x <= 0 and self.position.x == -1) or (self.rect.y >= 31 * TILE_SIZE[1] and self.position.y == 1) or (self.rect.y <= 0 and self.position.y == -1):
            speed = 0 #this checks for collisions with the borders of the map
            #self.position = (0,0)

        for barrelTest in OBJECTS: #a bit messy, might wanna have a second look
            if barrelTest:
                if self.position.y == -1 and barrelTest.rect.colliderect(self.rect.x, self.rect.y + - speed, self.rect.width , self.rect.height) :
                    self.position.x = 0
                    self.position.y = 0
                elif self.position.y == 1 and barrelTest.rect.colliderect(self.rect.x, self.rect.y + speed, self.rect.width, self.rect.height):
                    self.position.x = 0
                    self.position.y = 0
                elif self.position.x == -1 and barrelTest.rect.colliderect(self.rect.x - speed, self.rect.y, self.rect.width, self.rect.height):
                    self.position.x = 0
                    self.position.y = 0
                elif self.position.x == 1 and barrelTest.rect.colliderect(self.rect.x + speed, self.rect.y, self.rect.width, self.rect.height):
                    self.position.x = 0
                    self.position.y = 0

        self.rect.center += position * speed #pretty much this is the thing that moves the character


    def checkForWeaponDetection(self, events):
        for event in events:
            for weapon in WEAPONS_ON_MAP:
                if (weapon.rect.colliderect(self.rect.x + 20, self.rect.y + 20, self.rect.height + 20, self.rect.width + 20) and event.type == pygame.KEYDOWN and self.weapon != True and weapon.owner == ""):
                    if (event.key == pygame.K_e):
                        self.weapon = True
                        self.weaponId = weapon.id
                        weapon.owner = self.nickname
                        #print(f'OWNER: {weapon.owner}')
            
                if self.weapon == True and event.type == pygame.KEYDOWN and self.weaponId == weapon.id:
                    if event.key == pygame.K_q:
                        self.weapon = False
                        self.weaponId = 0
                        weapon.owner = ""
  
                #if self.weapon and weapon.owner == self.nickname:
                 #   weapon.rotateWeapon()
                  #  weapon.rect.x = self.rect.x + 35
                   # weapon.rect.y = self.rect.y + 35

    def healthDisplay(self):
        if self.isPlayable:
            healthText = get_font(30).render(f'Health:{self.health} ', True, "Red")
            healthRect = healthText.get_rect(center=(160,25))
            GAME_WINDOW.blit(healthText, healthRect)

    def ammoDisplay(self):
        if self.isPlayable:
            ammoText = get_font(30).render(f'Ammo:{self.ammo} ', True, "White")
            ammoRect = ammoText.get_rect(center=(WIDTH - 0.1 * WIDTH, HEIGHT - 0.95 * HEIGHT))
            GAME_WINDOW.blit(ammoText, ammoRect)
    
    def nicknameDisplay(self):
        nicknameText = get_font(18).render(self.nickname, True, "White")
        if self.isPlayable:
            nicknameRect = nicknameText.get_rect(center=(WIDTH / 2 + 20, HEIGHT / 2 - 70))
        else:
            nicknameRect = nicknameText.get_rect()
        GAME_WINDOW.blit(nicknameText, nicknameRect)
            
                
    def checkForHits(self):
        for bullet in BULLETS_ON_MAP:
            if bullet.rect.colliderect(self.rect.centerx, self.rect.centery, self.rect.height, self.rect.width) and bullet.shooter != self.nickname:
                self.health -= 1
                BULLETS_ON_MAP.remove(bullet)
                #print("REMOVED DUE TO HITS")
                spriteGroup.remove(bullet)

    def checkForHealth(self):
        if self.health == 0 and self in PLAYERS_ON_MAP:
            spriteGroup.remove(self)
            PLAYERS_ON_MAP.remove(self)

def checkIfShooting(events, client):
        ourPlayer = findPlayer()
        for event in events:
            for weapon in WEAPONS_ON_MAP:
                if event.type == pygame.MOUSEBUTTONDOWN and ourPlayer.ammo > 0 and ourPlayer.weapon and weapon.id == ourPlayer.weaponId:
                    client.sending_state = True
                    ourPlayer.ammo -= 1

##To Maximize the Window Size ONLY FOR WINDOWS
if sys.platform == "win32":
    HWND = pygame.display.get_wm_info()['window']
    SW_MAXIMIZE = 3
    ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)

class Weapon(pygame.sprite.Sprite): #IMPORTANT, write this thing in the brackets it is the inherentence thing you were talking about
    def __init__(self, posX, posY, group, id, owner):
        super().__init__(group) #IMPORTANT, RLY IMPORTANT without this line in the object, this implementation doesnt work
        self.image = pygame.image.load('sprites/weapons/pistol3.png')
        self.image_original = pygame.transform.scale(self.image, WEAPON_SIZE)
        self.rect = self.image.get_rect(topleft=(posX, posY))
        self.owner = ""
        self.id = id
        self.angle_to_rotate = 0
        WEAPONS_ON_MAP.append(self)
        
    def rotateWeapon(self):
        if self.owner == NICKNAME:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx, dy = mouse_x -  WIDTH/2, -(mouse_y - HEIGHT/2)
            self.angle_to_rotate = math.degrees(math.atan2(dy, dx))
        
        self.image = pygame.transform.rotate(self.image_original, self.angle_to_rotate)
        self.rect = self.image.get_rect(topleft=self.rect.center)  
        
    def updateWeaponPosition(self):
        for player in PLAYERS_ON_MAP:
            if player.nickname == self.owner:# and player.weapon:
                self.rotateWeapon()
                self.rect.x = player.rect.x + 35
                self.rect.y = player.rect.y + 35

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, group, shooter, id, angle = 0, onServer = False):
        super().__init__(group)
        self.position = pygame.math.Vector2()
        self.position.x = pos_x
        self.position.y = pos_y

        self.image= pygame.transform.scale(pygame.image.load('sprites/weapons/small_bullet2.png'), BULLET_SIZE)
        self.rect = self.image.get_rect(center = (pos_x, pos_y))

        self.bullet_speed = 5
        self.shooter = shooter
        self.id = id


        for player in PLAYERS_ON_MAP:
            if player.nickname == self.shooter:# and player.nickname != NICKNAME:
                self.angle_to_move = player.angle_pointing


     
        #mouse_x, mouse_y = pygame.mouse.get_pos()
        #dx, dy = mouse_x - WIDTH/2, -(mouse_y - HEIGHT/2)

        #self.angle_to_rotate = self.angle_to_move - 90

        #self.angle = math.degrees(math.atan2(dy, dx)) - 90
        self.angle = angle
        self.dx = math.cos(self.angle) * self.bullet_speed
        self.dy = math.sin(self.angle) * self.bullet_speed
        self.angle = math.degrees(-angle)

        self.image = pygame.transform.rotate(self.image, self.angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        
    
        #self.angle = angle
        #self.dx = math.cos(self.angle) * self.bullet_speed
        #self.dy = math.sin(self.angle) * self.bullet_speed




    def move(self):
        self.position.x += self.dx
        self.position.y += self.dy
        #print(f'BULLETS ARE MOVING BY: {self.position.x, self.position.y}')
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self.checkForCollisionWithObject()
        self.checkForCollisionWithBorder()
    
    def checkForCollisionWithObject(self):
        for object in OBJECTS:
            #print(OBJECTS)
            if object.rect.colliderect(self.rect.x, self.rect.y, self.rect.width,self.rect.height):
                BULLETS_ON_MAP.remove(self)
                if self in MY_BULLETS_ON_MAP:
                    MY_BULLETS_ON_MAP.remove(self)
            for bullet_info in MY_BULLETS_ON_MAP_INFO:
                if bullet_info.id == self.id:
                    MY_BULLETS_ON_MAP_INFO.remove(bullet_info)
            #print("REMOVED DUE TO OBJECT")
            spriteGroup.remove(self)

    
    def checkForCollisionWithBorder(self):
        if (self.rect.x >= 31 * TILE_SIZE[0]) or (self.rect.x <= 0) or (self.rect.y >= 31 * TILE_SIZE[1]) or (self.rect.y <= 0):
            BULLETS_ON_MAP.remove(self)
            if self in MY_BULLETS_ON_MAP:
                MY_BULLETS_ON_MAP.remove(self)
                for bullet_info in MY_BULLETS_ON_MAP_INFO:
                    if bullet_info.id == self.id:
                        MY_BULLETS_ON_MAP_INFO.remove(bullet_info)

            #print("REMOVED DUE TO BORDER")
            spriteGroup.remove(self)    

class ObjectBarrel(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('sprites\sci-fiPlatform\png\Objects\Barrel (1).png')
        self.image = pygame.transform.scale(self.image, BARREL_SIZE)
        self.rect = self.image.get_rect(topleft = pos)
        OBJECTS.append(self)

def drawWindow(events, spriteGroup, client):
    GAME_WINDOW.blit(BG, (0,0))

    for bullet in BULLETS_ON_MAP:
        #print("GOT TO MOVE MODULE")
        bullet.move()

    for weapon in WEAPONS_ON_MAP:
        weapon.updateWeaponPosition()

    checkIfShooting(events, client)
        #print(f'WEAPON OWNER: {weapon.owner}')
        #if weapon.owner == NICKNAME:
            #print(f'WeaponId: {weapon.id}, POSITION: {weapon.rect.center}')

    for player in PLAYERS_ON_MAP:
        player.updatePlayer(events, spriteGroup) #keeps track of inputs

    spriteGroup.cameraDraw() #the custom thing i di
    spriteGroup.update()#inherited from pygame.sprites.Group()
    #PLAYERS_ON_MAP.clear()
   # PLAYER_NICKNAMES.clear()
   # BULLETS_ON_MAP.clear()
   # WEAPONS_ON_MAP.clear()
    #OBJECTS.clear()
    #player2.updatePlayer(events, spriteGroup)

def drawCrosshair():
    x, y = pygame.mouse.get_pos()
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x + 6, y, 10, 4])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x - 12, y, 10, 4])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x, y + 6 , 4, 10])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x, y - 12 , 4, 10])

#print(NICKNAME)
client.sendHandshake(NICKNAME)

def findPlayer():
    for player in PLAYERS_ON_MAP:
       # print(player.nickname, player.isPlayable)
        if player.nickname == NICKNAME:
            ourPlayer = player
            return ourPlayer


threadIncoming = threading.Thread(target = client.handleIncomingServerInfoUpdate)

#time.sleep(1)
threadOutcoming = threading.Thread(target = client.sendInfoToServer)

def mainGameLoop():
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(FPS)
            events = pygame.event.get()  


            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                    client.sendDisconnection(NICKNAME)
                    os._exit(os.X_OK)
    
            for player in PLAYERS_ON_MAP:
                player.checkForWeaponDetection(events)#this can be called in the update player function in the object itself i think

            drawWindow(events, spriteGroup, client)
            drawCrosshair()
            pygame.display.update()
  


def main():
    threadIncoming.start()
    #mapDraw()
    threadOutcoming.start()
    pygame.mouse.set_visible(False)
    #spriteGroup.add(BG)
    mainGameLoop()
    pygame.quit()
    sys.exit()




if __name__ == "__main__":
    main()