import pygame
import os
import sys

pygame.init()

FPS = 60
SCREEN_INFO = pygame.display.Info()
WIDTH,HEIGHT = SCREEN_INFO.current_w, SCREEN_INFO.current_h
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
BG = (135,206,235)
ANIMATION_SPEED = 10
PLAYER_SIZE= [100, 100]
BARREL_SIZE = [300, 300]

class Object():
    def __init__(self):
        self.image = pygame.image.load('sprites\sci-fiPlatform\png\Objects\Barrel (1).png')
        self.image = pygame.transform.scale(self.image, BARREL_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 500

    def updateObject(self):
        pygame.draw.rect(GAME_WINDOW, (255 , 255, 255), self.rect) 
        GAME_WINDOW.blit(self.image, self.rect)

class Player():
    def __init__(self):
        self.imagesAnimationUp = []
        self.imagesAnimationDown = []
        self.imagesAnimationLeft = []
        self.imagesAnimationRight = []
        self.imageIndex = 0
        self.animationCooldown = 0
        self.position = ""

        for i in range(1, 4):
            image = pygame.image.load(f'sprites\player{i}.png')
            image = pygame.transform.scale(image, PLAYER_SIZE)
            if i == 1:
                self.rect = image.get_rect()
                self.rect.x = 300
                self.rect.y = 200
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
    

    def updatePlayer(self):
        PLAYER_SPEED_X = 0
        PLAYER_SPEED_Y = 0
        pygame.draw.rect(GAME_WINDOW, (255 , 255, 255), self.rect) 
        GAME_WINDOW.blit(self.image, self.rect)   

        keys = pygame.key.get_pressed()
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

        match self.position:
            case "UP":
                if testObject1.rect.colliderect(self.rect.x, self.rect.y + PLAYER_SPEED_Y, self.rect.width, self.rect.height):
                    print("a")
                    PLAYER_SPEED_Y = 0
            case "DOWN":
                if testObject1.rect.colliderect(self.rect.x, self.rect.y + PLAYER_SPEED_Y, self.rect.width, self.rect.height):
                    print("a")
                    PLAYER_SPEED_Y = 0
            case "LEFT":
                if testObject1.rect.colliderect(self.rect.x + PLAYER_SPEED_X, self.rect.y, self.rect.width, self.rect.height):
                    print("a")
                    PLAYER_SPEED_X = 0 
            case "RIGHT":
                if testObject1.rect.colliderect(self.rect.x + PLAYER_SPEED_X, self.rect.y, self.rect.width, self.rect.height):
                    print("a")
                    PLAYER_SPEED_X = 0

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
        match self.position:
            case "UP":
                self.rect.y += PLAYER_SPEED_Y
            case "DOWN":
                self.rect.y += PLAYER_SPEED_Y
            case "LEFT":
                self.rect.x += PLAYER_SPEED_X
            case "RIGHT":
                self.rect.x += PLAYER_SPEED_X


def drawWindow():
    GAME_WINDOW.fill(BG)
    player1.updatePlayer()
    testObject1.updateObject()

player1 = Player()
testObject1 = Object()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        drawWindow()
        pygame.display.update()

             
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()