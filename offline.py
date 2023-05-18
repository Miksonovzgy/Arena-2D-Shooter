import pygame
import os
import sys
import ctypes
import time


pygame.init()


FPS = 60
SCREEN_INFO = pygame.display.Info()
WIDTH,HEIGHT = SCREEN_INFO.current_w, SCREEN_INFO.current_h
GAME_WINDOW = pygame.display.set_mode((WIDTH - 20, HEIGHT - 20), pygame.RESIZABLE)

BG = (135,206,235)
ANIMATION_SPEED = 10
PLAYER_SIZE= [100, 100]
BARREL_SIZE = (177/3, 238/3)
WEAPON_SIZE = (412/7,166/7)
BULLET_SIZE = (32/3, 80/3)


##To Maximize the Window Size ONLY FOR WINDOWS
if sys.platform == "win32":
    HWND = pygame.display.get_wm_info()['window']
    SW_MAXIMIZE = 3
    ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)

class Object():
    def __init__(self):
        self.image = pygame.image.load('sprites\sci-fiPlatform\png\Objects\Barrel (1).png')
        self.image = pygame.transform.scale(self.image, BARREL_SIZE)
        self.rect = pygame.Rect(500, 500, 177/3, 238/3)
        self.rect.x = 500
        self.rect.y = 500

    def updateObject(self):
        GAME_WINDOW.blit(self.image, self.rect)


class Weapon():
    def __init__(self):
        self.image = pygame.image.load('sprites/weapons/pistol3.png')
        self.image = pygame.transform.scale(self.image, WEAPON_SIZE)
        self.rect = pygame.Rect(700, 700, 412/7, 166/7)
        self.rect.x = 700
        self.rect.y = 700
    
    
    def updateWeapon(self):
        GAME_WINDOW.blit(self.image, self.rect)


class Bullet():
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load('sprites/weapons/small_bullet2.png'), BULLET_SIZE)
        self.rect = pygame.Rect
        




class Player():
    def __init__(self):
        self.imagesAnimationUp = []
        self.imagesAnimationDown = []
        self.imagesAnimationLeft = []
        self.imagesAnimationRight = []
        self.imageIndex = 0
        self.animationCooldown = 0
        self.position = ""
        self.weapon = False
        self.ammo = []
        self.health = []

        for i in range(1, 4):
            image = pygame.image.load(f'sprites\player{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            if i == 1:
                self.rect = pygame.Rect(200, 300, PLAYER_SIZE[0], PLAYER_SIZE[1])
            self.imagesAnimationUp.append(image)

        self.imagesAnimationDown = []

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
    

    def updatePlayer(self, keys):
        PLAYER_SPEED_X = 0
        PLAYER_SPEED_Y = 0 
        GAME_WINDOW.blit(self.image, self.rect)   


        #handling Movement
        if keys[pygame.K_w] and self.rect.y > 0:
            PLAYER_SPEED_Y = -15
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationUp[self.imageIndex]
                self.animationCooldown = 0
            self.position = "UP"
            
        if keys[pygame.K_s] and self.rect.y + self.rect.height < HEIGHT:
            PLAYER_SPEED_Y = 15
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationDown[self.imageIndex]
                self.animationCooldown = 0
            self.position = "DOWN"

        if keys[pygame.K_d] and self.rect.x + self.rect.width < WIDTH:
            PLAYER_SPEED_X = 15
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationRight[self.imageIndex]
                self.animationCooldown = 0
            self.position = "RIGHT"

        if keys[pygame.K_a] and self.rect.x > 0:
            PLAYER_SPEED_X = -15
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationLeft[self.imageIndex]
                self.animationCooldown = 0
            self.position = "LEFT"

        #colliding with objects
        match self.position:
            case "UP":
                if testObject1.rect.colliderect(self.rect.x, self.rect.y + PLAYER_SPEED_Y, self.rect.width, self.rect.height):
                    PLAYER_SPEED_Y = 0
            case "DOWN":
                if testObject1.rect.colliderect(self.rect.x, self.rect.y + PLAYER_SPEED_Y, self.rect.width, self.rect.height):
                    PLAYER_SPEED_Y = 0
            case "LEFT":
                if testObject1.rect.colliderect(self.rect.x + PLAYER_SPEED_X, self.rect.y, self.rect.width, self.rect.height):
                    PLAYER_SPEED_X = 0 
            case "RIGHT":
                if testObject1.rect.colliderect(self.rect.x + PLAYER_SPEED_X, self.rect.y, self.rect.width, self.rect.height):
                    PLAYER_SPEED_X = 0

        #Handling animations when stopped
        if keys[pygame.K_w] == False and keys[pygame.K_s] == False and keys[pygame.K_a] == False and keys[pygame.K_d] == False:
            match self.position:
                case "UP":
                    self.imageIndex = 0
                    self.image = self.imagesAnimationUp[self.imageIndex]
                case "DOWN":
                    self.imageIndex = 0
                    self.image = self.imagesAnimationDown[self.imageIndex] 
                case "LEFT":
                    self.imageIndex = 0
                    self.image = self.imagesAnimationLeft[self.imageIndex] 
                case "RIGHT":
                    self.imageIndex = 0
                    self.image = self.imagesAnimationRight[self.imageIndex]

        #Movement of the Player Rectangle
        match self.position:
            case "UP":
                self.rect.y += PLAYER_SPEED_Y
            case "DOWN":
                self.rect.y += PLAYER_SPEED_Y
            case "LEFT":
                self.rect.x += PLAYER_SPEED_X
            case "RIGHT":
                self.rect.x += PLAYER_SPEED_X



    

    def checkForWeaponDetection(self, events):
        for event in events:
            if testWeapon1.rect.colliderect(self.rect.x + 20, self.rect.y + 20, self.rect.height + 20, self.rect.width + 20) and event.type == pygame.KEYDOWN and self.weapon != True:
                if(event.key == pygame.K_e):
                    self.weapon = True
            
            if self.weapon == True and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.weapon = False
                
                
        if self.weapon:
            testWeapon1.rect.x = self.rect.x + 65
            testWeapon1.rect.y = self.rect.y + 55

        

        





def drawWindow(keys):
    GAME_WINDOW.fill(BG)
    player1.updatePlayer(keys)
    testObject1.updateObject()
    testWeapon1.updateWeapon()

def drawCrosshair():
    x, y = pygame.mouse.get_pos()
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x + 6, y, 10, 4])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x - 12, y, 10, 4])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x, y + 6 , 4, 10])
    pygame.draw.rect(GAME_WINDOW, (255,0,0), [x, y - 12 , 4, 10])


player1 = Player()
testObject1 = Object()
testWeapon1 = Weapon()

def main():
    clock = pygame.time.Clock()
    run = True

    pygame.mouse.set_visible(False)
    while run:
        clock.tick(FPS)
        events = pygame.event.get()    
        userInput = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                run = False
    

        player1.checkForWeaponDetection(events)
        drawWindow(userInput)
        drawCrosshair()
        pygame.display.update()

             
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()