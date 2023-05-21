


#####IMPORTANT#####
#this version is technically ocmpatible with the new client.py however it doesnt work as it should









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




class CameraGroup(pygame.sprite.Group): #this essentially draws the screen and what you are seeing right now, hence why it has replaced every image creation
    def __init__(self):                 #STRONGLY RECOMMEND: SEE HOW I MAKE IMAGES WITH THIS AND MAKE THE OTHER OBJECTS THE SAME WAY
        super().__init__()
        self.displayScreen = pygame.display.get_surface()
        self.cameraX = self.displayScreen.get_size()[0]/2
        self.cameraY = self.displayScreen.get_size()[1]/2
        self.offset = pygame.math.Vector2() #this is for centering
        self.cameraRect = pygame.Rect(200, 100, self.displayScreen.get_size()[0] - (200 + 200), self.displayScreen.get_size()[1] - (100 + 100)) #TO DO: replace with constants

    def cameraDraw(self, player): #this is the important stuff, im essentially modyfing the draw function here

        self.offset.x = player.rect.centerx - self.cameraX
        self.offset.y = player.rect.centery - self.cameraY #this is for centering

        for sprite in self.sprites(): #draws every sprite (which for now is pistol, barrel and player)
            offsetPosition = sprite.rect.topleft - self.offset
            self.displayScreen.blit(sprite.image, offsetPosition)

spriteGroup = CameraGroup() #this makes the custom group of sprites




#NOT NEEDED FOR NOW
class Background(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load("sprites\sci-fiPlatform\png\Tiles\Acid (2).png")
        self.image = pygame.transform.scale(BG,(WIDTH, HEIGHT))
        self.rect = self.image.get_rect()

#BG = Background(spriteGroup)

#tileSpriteGroup = pygame.sprite.Group()


def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


class Tile(pygame.sprite.Sprite): #WATCH TUTORIAL
    def __init__(self, pos, surf: pygame.Surface, group): #,group
        super().__init__(group) #group
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, nickname):
        super().__init__(group)
        self.group = group
        self.imagesAnimationUp = []
        self.imagesAnimationDown = []
        self.imagesAnimationLeft = []
        self.imagesAnimationRight = []
        self.imageIndex = 0
        self.animationCooldown = 0
        self.position = pygame.math.Vector2() #movement physics is a bit changed now, i think its smoother
        self.speed = 30
        self.weapon = False
        self.weaponId = 0
        self.ammo = 500
        self.health = 3
        self.nickname = nickname
        self.isPlayable = False
        PLAYERS_ON_MAP.append(self)

        for i in range(1, 4):
            image = pygame.image.load(f'sprites/player{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            if i == 1:
                self.rect = image.get_rect(topleft = pos)
                self.rect.width = self.rect.width - 35
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

        if not self.isPlayable:
            self.rect.x = pos[0]
            self.rect.y = pos[1]


    
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
        
        else:
            self.position.x = x
            self.position.y = y


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

        self.checkIfShooting(events, spriteGroup)
        self.playerInput(1, 0)
        self.animations()
        self.checkForHits()
        self.checkForHealth()
        self.healthDisplay()
        self.nicknameDisplay()
        self.ammoDisplay()
        

        speed = self.speed
        position = self.position

        if (self.rect.x >= 31 * TILE_SIZE[0] and self.position.x == 1) or (self.rect.x <= 0 and self.position.x == -1) or (self.rect.y >= 31 * TILE_SIZE[1] and self.position.y == 1) or (self.rect.y <= 0 and self.position.y == -1):
            speed = 0 #this checks for collisions with the borders of the map

        for barrelTest in OBJECTS: #a bit messy, might wanna have a second look
            if barrelTest:
                if self.position.y == -1 and barrelTest.rect.colliderect(self.rect.x, self.rect.y + - speed, self.rect.width , self.rect.height) :
                    speed = 0
                elif self.position.y == 1 and barrelTest.rect.colliderect(self.rect.x, self.rect.y + speed, self.rect.width, self.rect.height):
                    speed = 0
                elif self.position.x == -1 and barrelTest.rect.colliderect(self.rect.x - speed, self.rect.y, self.rect.width, self.rect.height):
                    speed = 0
                elif self.position.x == 1 and barrelTest.rect.colliderect(self.rect.x + speed, self.rect.y, self.rect.width, self.rect.height):
                    speed = 0

        self.rect.center += position * speed #pretty much this is the thing that moves the character


    def checkForWeaponDetection(self, events):
        for event in events:
            for weapon in WEAPONS_ON_MAP:
                if (weapon.rect.colliderect(self.rect.x + 20, self.rect.y + 20, self.rect.height + 20, self.rect.width + 20) and event.type == pygame.KEYDOWN and self.weapon != True and weapon.owner == ""):
                    if (event.key == pygame.K_e):
                        self.weapon = True
                        self.weaponId = weapon.id
                        weapon.owner = self.nickname
            
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
            

    def checkIfShooting(self, events, spriteGroup):
            for event in events:
                for weapon in WEAPONS_ON_MAP:
                    if event.type == pygame.MOUSEBUTTONDOWN and self.ammo > 0 and self.weapon and weapon.id == self.weaponId:
                        bullet = Bullet(weapon.rect.x, weapon.rect.y, spriteGroup, self.nickname)
                        BULLETS_ON_MAP.append(bullet)
                        self.ammo -= 1
                
    def checkForHits(self):
        for bullet in BULLETS_ON_MAP:
            if bullet.rect.colliderect(self.rect.centerx, self.rect.centery, self.rect.height, self.rect.width) and bullet.shooter != self.nickname:
                self.health -= 1
                BULLETS_ON_MAP.remove(bullet)
                spriteGroup.remove(bullet)

    def checkForHealth(self):
        if self.health == 0 and self in PLAYERS_ON_MAP:
            spriteGroup.remove(self)
            PLAYERS_ON_MAP.remove(self)


class Weapon(pygame.sprite.Sprite): #IMPORTANT, write this thing in the brackets it is the inherentence thing you were talking about
    def __init__(self, pos, group, id):
        super().__init__(group) #IMPORTANT, RLY IMPORTANT without this line in the object, this implementation doesnt work
        self.image = pygame.image.load('sprites/weapons/pistol3.png')
        self.image_original = pygame.transform.scale(self.image, WEAPON_SIZE)
        self.rect = self.image.get_rect(center=pos)
        self.owner = ""
        self.id = id
        WEAPONS_ON_MAP.append(self)
        
    def rotateWeapon(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x -  WIDTH/2, -(mouse_y - HEIGHT/2)
        angle = math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.image_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def updateWeaponPosition(self):
        for player in PLAYERS_ON_MAP:
            if player.nickname == self.owner and player.weapon:
                self.rotateWeapon()
                self.rect.x = player.rect.x + 35
                self.rect.y = player.rect.y + 35

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, group, shooter):
        super().__init__(group)
        self.position = pygame.math.Vector2()
        self.position.x = pos_x
        self.position.y = pos_y
        self.image_original = pygame.transform.scale(pygame.image.load('sprites/weapons/small_bullet2.png'), BULLET_SIZE)
        self.rect = self.image_original.get_rect(center = (pos_x, pos_y))
        self.bullet_speed = 60
        self.shooter = shooter

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - WIDTH/2, -(mouse_y - HEIGHT/2)
        angle = math.degrees(math.atan2(dy, dx)) - 90

        self.image = pygame.transform.rotate(self.image_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


        self.angle_to_move = math.atan2(mouse_y - HEIGHT/2, mouse_x - WIDTH/2)
        self.dx = math.cos(self.angle_to_move) * self.bullet_speed
        self.dy = math.sin(self.angle_to_move) * self.bullet_speed

    def move(self):
        self.position.x += self.dx
        self.position.y += self.dy
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self.checkForCollisionWithObject()
        self.checkForCollisionWithBorder()
    
    def checkForCollisionWithObject(self):
        for object in OBJECTS:
            if object.rect.colliderect(self.rect.x, self.rect.y, self.rect.width,self.rect.height):
                BULLETS_ON_MAP.remove(self)
                spriteGroup.remove(self)

    
    def checkForCollisionWithBorder(self):
        if (self.rect.x >= 31 * TILE_SIZE[0]) or (self.rect.x <= 0) or (self.rect.y >= 31 * TILE_SIZE[1]) or (self.rect.y <= 0):
            BULLETS_ON_MAP.remove(self)
            spriteGroup.remove(self)    

class ObjectBarrel(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('sprites\sci-fiPlatform\png\Objects\Barrel (1).png')
        self.image = pygame.transform.scale(self.image, BARREL_SIZE)
        self.rect = self.image.get_rect(topleft = pos)


