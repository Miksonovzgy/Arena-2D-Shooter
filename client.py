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
from offline import Weapon as Weapon
from offline import Player as Player
from offline import CameraGroup as CameraGroup
from offline import Background as Background
from offline import Tile as Tile
from offline import Bullet as Bullet
from offline import ObjectBarrel as ObjectBarrel





pygame.init()
OBJECTS = []
FPS = 60
SCREEN_INFO = pygame.display.Info()
WIDTH,HEIGHT = 1280,720
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
BG = pygame.image.load("sprites\sci-fiPlatform\png\Tiles\Acid (2).jpg")
BG = pygame.transform.scale(BG,(WIDTH, HEIGHT))
ANIMATION_SPEED = 5
PLAYER_SIZE= [100, 100]
BARREL_SIZE = (177/3, 238/3)
WEAPON_SIZE = (412/7,166/7)
BULLET_SIZE = (32/3, 80/3)
TILE_SIZE = [128, 120]
BULLETS_ON_MAP = []
PLAYERS_ON_MAP = []
WEAPONS_ON_MAP = []
MAP_INDEX = 1


def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


spriteGroup = CameraGroup()


##To Maximize the Window Size ONLY FOR WINDOWS
if sys.platform == "win32":
    HWND = pygame.display.get_wm_info()['window']
    SW_MAXIMIZE = 3
    ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)

class ClientSide():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = "localhost"
        self.port = 9999
        self.address = (self.server, self.port)
    
    def sendHandshake(self, nickname):
        newPlayerInfo = infoObjects.disconnectionObject(nickname, "NAME")
        newPlayerObject = pickle.dumps(newPlayerInfo)
        self.client.sendto(newPlayerObject, self.address)

    def receiveHandshake(self):
        message, _ = self.client.recvfrom(1024)
        infoFromServer = pickle.loads(message)
        return infoFromServer

    def handleIncomingInfoHandshake(self):
        infoFromServer = self.receiveHandshake()
        print("received")
        if len(PLAYERS_ON_MAP) == 0:
            for newPlayer in infoFromServer.playerList:
                newPlayer = Player(newPlayer.pos, spriteGroup, newPlayer.nickname)





client = ClientSide()
nickname = "mikołaj2" #input("Input Nickname: ")

TMX_DATA = load_pygame(f'map{MAP_INDEX}Test.tmx') #IMPORTANT: dont forget to change map collisions after chaning the map




def mapDraw(): #WATCH TUTORIAL      
    for tiles in TMX_DATA.layers:
        if hasattr(tiles, 'data'):
            for x,y,surf in tiles.tiles():
                pos = (x * TILE_SIZE[0], y * TILE_SIZE[1])
                Tile(pos = pos, surf = surf, group = spriteGroup)#tileSpriteGroup)


def drawWindow(events, spriteGroup, weapon):
    for bullet in BULLETS_ON_MAP:
        bullet.move()
    
    for weapon in WEAPONS_ON_MAP:
        weapon.updateWeaponPosition()

    GAME_WINDOW.blit(BG, (0,0))
    spriteGroup.update() #inherited from pygame.sprites.Group()


    for player in PLAYERS_ON_MAP:
        player.updatePlayer(events, spriteGroup) #keeps track of inputs

        if player.isPlayable:
            spriteGroup.cameraDraw(player) #the custom thing i did
    #player2.updatePlayer(events, spriteGroup)


def drawCrosshair():
    x, y = pygame.mouse.get_pos()
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x + 6, y, 10, 4])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x - 12, y, 10, 4])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x, y + 6 , 4, 10])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x, y - 12 , 4, 10])
        

client.sendHandshake(nickname)
client.handleIncomingInfoHandshake()

print(PLAYERS_ON_MAP)


mapDraw()
#player1 = Player((1000, 900), spriteGroup, nickname)
#player2 = Player((0, 900), spriteGroup, "TEST")

for player in PLAYERS_ON_MAP:
    if(player.nickname == nickname):
        player.isPlayable = True


#player1.isPlayable = True
#player2.speed = 5               ##DEBUGGING PURPOSES
testObject1 = ObjectBarrel((200, 200), spriteGroup)
OBJECTS.append(testObject1)#saving the barrel in a list tocheck for collisions, ideally this will be a lit of static objects and even more ideally we can check only for the close ones in the Player object
testWeapon1 = Weapon((300, 300), spriteGroup, 1)
testWeapon2 = Weapon((900, 900), spriteGroup, 2)
testWeapon3 = Weapon((500, 500), spriteGroup, 3)
testWeapon4 = Weapon((700, 700), spriteGroup, 4)

#def main():
    clock = pygame.time.Clock()
    run = True

    pygame.mouse.set_visible(False)
    #spriteGroup.add(BG)
    while run:
        clock.tick(FPS)
        events = pygame.event.get()    

        for event in events:
            if event.type == pygame.QUIT:
                run = False
    
        for player in PLAYERS_ON_MAP:
            player.checkForWeaponDetection(events)#this can be called in the update player function in the object itself i think

        drawWindow(events, spriteGroup, testWeapon1)
        drawCrosshair()
        pygame.display.update()

             
    pygame.quit()
    sys.exit()



#if __name__ == "__main__":
#    main()
       








