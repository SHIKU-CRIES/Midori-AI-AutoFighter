
import pygame

class Screen:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA)