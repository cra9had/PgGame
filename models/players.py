import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.health_capacity = 10
        self.current_health = self.health_capacity
        self.image = pg.image.load("sprites/Earth.png").convert_alpha()
        self.image = pg.transform.scale(self.image, size)
        self.view_image = self.image
        self.rect = pg.Rect((pos[0], pos[1], size[0], size[1]))
        self.mask = pg.mask.from_surface(self.view_image)
        self.angle = 0

    def rotate(self):
        self.angle -= 1
        loc = self.rect.center
        self.view_image = pg.transform.rotate(self.image, self.angle)
        self.rect = self.view_image.get_rect()
        self.rect.center = loc
        self.mask = pg.mask.from_surface(self.view_image)
