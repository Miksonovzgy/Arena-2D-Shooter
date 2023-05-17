import pygame
import os

FPS = 60
HEIGHT = 500
WIDTH = 500
GAME_WINDOW = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
BG = (135,206,235)

randomObjectForMapTesting1 = pygame.image.load('sprites\sci-fiPlatform\png\Objects\Barrel (1).png')
playerTest1 = pygame.image.load('sprites\player.png')

def drawWindow():
    GAME_WINDOW.fill(BG)
    GAME_WINDOW.blit(randomObjectForMapTesting1, (500, 500))
    GAME_WINDOW.blit(playerTest1, (200, 200))
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        drawWindow()
    pygame.quit()



if __name__ == "__main__":
    main()