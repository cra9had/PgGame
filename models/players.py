import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.health_capacity = 6
        self.current_health = self.health_capacity
        self.images = [pg.image.load("sprites/Earth.png").convert_alpha(),
                       pg.image.load("sprites/Broken_Earth1.png").convert_alpha(),
                       pg.image.load("sprites/Broken_Earth2.png").convert_alpha()]
        for i, img in enumerate(self.images):
            self.images[i] = pg.transform.scale(img, size)
        self.current_image = self.images[0]
        self.view_image = self.current_image
        self.rect = pg.Rect((pos[0], pos[1], size[0], size[1]))
        self.mask = pg.mask.from_surface(self.view_image)
        self.angle = 0

    def process(self):
        if self.current_health <= self.health_capacity * (2/3):
            self.current_image = self.images[1]
        if self.current_health <= self.health_capacity * (1/3):
            self.current_image = self.images[2]

    def rotate(self):
        self.angle -= 1
        loc = self.rect.center
        self.view_image = pg.transform.rotate(self.current_image, self.angle)
        self.rect = self.view_image.get_rect()
        self.rect.center = loc
        self.mask = pg.mask.from_surface(self.view_image)
