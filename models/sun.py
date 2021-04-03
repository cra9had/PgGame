import pygame as pg


class Sun(pg.sprite.Sprite):
    def __init__(self, size, pos):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/sun.png").convert_alpha()
        self.image = pg.transform.scale(self.image, size)
        self.rect = pg.Rect(pos + size)
        self.mask = pg.mask.from_surface(self.image)

    def move(self):
        mouse_pos = pg.mouse.get_pos()
        self.rect.x = mouse_pos[0] - self.rect.width // 2
        self.rect.y = mouse_pos[1] - self.rect.height // 2

