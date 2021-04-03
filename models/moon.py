import pygame as pg
import math


class Moon(pg.sprite.Sprite):
    def __init__(self, size, pos, radius):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/moon.png").convert_alpha()
        self.image = pg.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.radius = radius
        self.pos = pos
        self.angle = 0
        self.mask = pg.mask.from_surface(self.image)

    def rotate(self):
        angle = math.radians(self.angle)
        self.rect.x = self.radius * math.cos(angle) + self.pos[0]
        self.rect.y = self.radius * math.sin(angle) + self.pos[1]
        self.angle += 2

