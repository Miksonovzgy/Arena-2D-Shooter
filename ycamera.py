import pygame
import os
import sys
import ctypes
import time
from pytmx.util_pygame import load_pygame
pygame.init()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.displayScreen = pygame.display.get_surface()
    
    def cameraDraw(self):
        for sprite in self.sprites():
            self.displayScreen.blit(sprite.image, sprite.rect)