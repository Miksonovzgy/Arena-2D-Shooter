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
PLAYER_SPEED = 15
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
        GAME_WINDOW.blit(self.image, self.rect)

def detectCollision(rectangle: pygame.Rect, rectangle2: pygame.Rect):
    if rectangle.colliderect(rectangle2):
       # print(False)
        return False
    else: 
       # print(True)
        return True

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
        GAME_WINDOW.blit(self.image, self.rect)    

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.y > 0:
            self.rect.y -= PLAYER_SPEED
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationUp[self.imageIndex]
                self.animationCooldown = 0
            self.position = "UP"
            
        if keys[pygame.K_s] and self.rect.y + self.rect.height < HEIGHT:
            self.rect.y += PLAYER_SPEED
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationDown[self.imageIndex]
                self.animationCooldown = 0
            self.position = "DOWN"

        if keys[pygame.K_d] and self.rect.x + self.rect.width < WIDTH:
            self.rect.x += PLAYER_SPEED
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationRight[self.imageIndex]
                self.animationCooldown = 0
            self.position = "RIGHT"

        if keys[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= PLAYER_SPEED
            self.animationCooldown += 1
            if self.animationCooldown == ANIMATION_SPEED:
                self.imageIndex += 1
                if (self.imageIndex == 3):
                    self.imageIndex = 0
                self.image = self.imagesAnimationLeft[self.imageIndex]
                self.animationCooldown = 0
            self.position = "LEFT"

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


                 

def drawWindow():
    GAME_WINDOW.fill(BG)

def main():
    clock = pygame.time.Clock()
    run = True
    player1 = Player()
    testObject1 = Object()
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        drawWindow()
        player1.updatePlayer()
        testObject1.updateObject()
        if player1.rect.colliderect(testObject1.rect):
            print("a")
        else:
            print("b")
        pygame.display.update()

             
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()