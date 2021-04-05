import pygame as pg


class ShopButton(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/shop_btn.png").convert_alpha()
        self.image = pg.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


class Shop:
    def __init__(self, sc, font):
        self.items = {
            'moon': {"cost": 5000,
                     "image": "moon_image",
                     "on": False,
                     "bought": False}
        }

        self.images = {"moon_image": pg.transform.scale(pg.image.load("sprites/moon.png").convert_alpha(), [100, 100])}

        self.sc = sc
        self.border_px = 50
        self.font = font
        self.one_letter_size = 25
        self.current_item = -1

    def _calc_text_pos(self, start, end, letters):
        letters_px = letters * self.one_letter_size
        all_px = end - start
        current_px = (all_px - letters_px) // 2
        return current_px + start + 1

    def render(self, current_money):
        self.current_item = -1
        for i, item in enumerate(self.items.values()):
            self.sc.blit(self.images[item['image']], [i * 100 + self.border_px, i + self.border_px])

            mouse_pos = pg.mouse.get_pos()

            item_rect = pg.Rect([i*100 + self.border_px - 5, i*100 + self.border_px - 5, 100 + 10, 120 + 41])

            if item_rect.collidepoint(mouse_pos):
                pg.draw.rect(self.sc, (255, 255, 255), item_rect, 1)
                self.current_item = i

            if item['bought']:
                color = (0, 0, 255)
            elif current_money < item['cost']:
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)

            self.sc.blit(self.font.render(f"{item['cost']}$", False, color),
                         [self._calc_text_pos(i * 100 + self.border_px, i * 100 + self.border_px + 100,
                                              len(str(item['cost']))), i + self.border_px + 120])
