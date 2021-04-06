import pygame as pg


class Button:
    def __init__(self, pos, size, text):
        font = pg.font.Font("fonts/pixel.ttf", size)
        self.text = font.render(text, False, (255, 255, 255))
        self.rect = self.text.get_rect(center=pos)
