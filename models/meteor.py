import pygame as pg
import math


class Meteor(pg.sprite.Sprite):
    def __init__(self, pos, size, speed, target_pos):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/meteor.png").convert_alpha()
        self.image = pg.transform.scale(self.image, size)
        self.rect = pg.Rect((pos[0], pos[1], size[0], size[1]))
        self.angle = math.degrees(math.atan2(target_pos[1] - self.rect.center[1], target_pos[0] - self.rect.center[0]))
        loc = self.rect.center
        self.image = pg.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = loc
        self.angle = math.radians(self.angle)
        self.speed = speed
        self.mask = pg.mask.from_surface(self.image)

    def move(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)
        # keys = pg.key.get_pressed()
        # if keys[pg.K_a]:
        #     self.rect.x -= self.speed
        # elif keys[pg.K_d]:
        #     self.rect.x += self.speed
        # elif keys[pg.K_s]:
        #     self.rect.y += self.speed
        # elif keys[pg.K_w]:
        #     self.rect.y -= self.speed
