import pygame as pg
import pygame_gui
import random
import math

from models.players import Player
from models.meteor import Meteor
from models.sun import Sun
from models.shop import Shop, ShopButton
from models.moon import Moon

from particle import Emitter
from winreg import *


class Game:
    WIDTH, HEIGHT = 1000, 750
    FPS = 60
    SPAWNAMETEOR = pg.USEREVENT + 1
    TIMER = pg.USEREVENT + 2

    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.sc = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), "theme.json")
        self.clock = pg.time.Clock()
        self.player = Player([self.WIDTH // 2 - 100, self.HEIGHT // 2 - 100], [200, 200])
        self.meteors = pg.sprite.Group()
        self.money_for_meteor = range(1, 4)
        self.sun = Sun([50, 50], [self.WIDTH // 2 - 25, self.HEIGHT // 2 - 25])
        self.shop_btn = ShopButton([0, self.HEIGHT - 50], [57, 50])
        self.moon = Moon([125, 125], [self.WIDTH // 2 - 62.5, self.HEIGHT // 2 - 62.5], 250)
        self.fire_particle = self.get_fire_particle()
        self.particles = []
        self.ticks = pg.time.get_ticks()

        self.font_arial = pg.font.Font('fonts/pixel.ttf', 36)

        self.shop_sys = Shop(self.sc, self.font_arial)
        self.shop_sys.items = self.get_shop_sys_items()

        self.bg = pg.image.load("sprites/bg.jpeg").convert_alpha()
        self.game_over_image = pg.image.load("sprites/game_over.png").convert_alpha()

        self.health_bar = pygame_gui.elements.UIScreenSpaceHealthBar(relative_rect=pg.Rect(self.WIDTH - 200,
                                                                                           self.HEIGHT - 20,
                                                                                           200, 20),
                                                                     manager=self.manager,
                                                                     sprite_to_monitor=self.player)

        self.tab_is_pressed = False
        self.pause = False
        self.game_over = False
        self.spawn_meteor_time = 1000
        self.timer = 0
        pg.time.set_timer(self.SPAWNAMETEOR, self.spawn_meteor_time)  # 1 sec
        pg.time.set_timer(self.TIMER, 1000)  # 1 sec
        self.spawned_meteor = 0
        self.money = self.get_money()
        self.money_text = self.font_arial.render(f"{self.money}$", False, (255, 255, 255))
        self.timer_text = self.font_arial.render("00:00", False, (255, 255, 255))

    def get_shop_sys_items(self):
        try:
            aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
            aKey = OpenKey(aReg, r"Software\\SaveTheEarth")
            return eval(EnumValue(aKey, 0)[1])
        except (FileNotFoundError, OSError):
            CreateKey(HKEY_CURRENT_USER, r'Software\\SaveTheEarth')
            self.registry_set_key(HKEY_CURRENT_USER, r'Software\\SaveTheEarth', 'items', REG_SZ,
                                  f"{self.shop_sys.items}")
            return self.shop_sys.items

    def get_money(self):
        try:
            aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
            aKey = OpenKey(aReg, r"Software\\SaveTheEarth")
            return int(EnumValue(aKey, 1)[1])
        except (FileNotFoundError, OSError):
            CreateKey(HKEY_CURRENT_USER, r'Software\\SaveTheEarth')
            self.registry_set_key(HKEY_CURRENT_USER, r'Software\\SaveTheEarth', 'money', REG_SZ, "0")
            return 0

    @staticmethod
    def registry_set_key(hive, register_path, key, register_type, value):
        try:
            reg = OpenKey(hive, register_path, 0, KEY_ALL_ACCESS)
        except EnvironmentError:
            try:
                reg = CreateKey(hive, register_path, 0, KEY_ALL_ACCESS)
                SetValueEx(reg, key, None, register_type, value)
                CloseKey(reg)
            except:
                return
            return
        try:
            if QueryValue(reg, key) == value:
                return
            else:
                SetValueEx(reg, key, None, register_type, value)  # added
        except:
            SetValueEx(reg, key, None, register_type, value)
        CloseKey(reg)

    def get_fire_particle(self):
        kwarg_dict = {"texture": pg.image.load("sprites/fuzzball.png").convert_alpha(),
                      "angle": (math.pi / 3, 2 * math.pi / 3),
                      "speed": (0.1, 0.5),
                      "size": (15, 20),
                      "life_span": 1.0,
                      "start_color": (255, 50, 15)}
        return Emitter([self.WIDTH // 2, self.HEIGHT // 2], 150, **kwarg_dict)

    def restart_game(self):
        self.player.current_health = self.player.health_capacity
        self.player.current_image = self.player.images[0]
        self.timer = 0
        self.particles = []
        self.meteors = pg.sprite.Group()

    def draw_scene(self):
        # pg.draw.circle(self.sc, (0, 255, 0), [self.player.rect.x, self.player.rect.y], self.player.rect[3])
        self.sc.blit(self.bg, (0, 0))
        if self.game_over:
            size = self.game_over_image.get_size()
            self.sc.blit(self.game_over_image, ((self.WIDTH // 2) - (size[0] // 2), (self.HEIGHT // 2) - (size[1] // 2)))
            return
        self.sc.blit(self.player.view_image, [self.player.rect.x, self.player.rect.y])
        pg.draw.rect(self.sc, (255, 0, 0), [self.player.rect.x, self.player.rect.y,
                                            self.player.rect[2], self.player.rect[3]], 2)
        self.draw_meteors()

        if self.shop_sys.items['moon']['bought'] and self.shop_sys.items['moon']['on']:
            self.sc.blit(self.moon.image, [self.moon.rect.x, self.moon.rect.y])

        self.sc.blit(self.sun.image, self.sun.rect)

        self.draw_particles()
        self.sc.blit(self.money_text, (0, 0))
        self.sc.blit(self.timer_text, (self.WIDTH - 36 * 5, 0))
        self.sc.blit(self.shop_btn.image, [self.shop_btn.rect.x, self.shop_btn.rect.y])

        # pg.draw.circle(self.sc, (0, 255, 0), self.moon.pos, 5)

    def draw_particles(self):
        for particle in self.particles:
            pg.draw.circle(self.sc, (255, 80, 0), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

    def get_random_pos(self):
        if random.randint(0, 1) == 0:
            return random.randint(0, self.WIDTH), random.choice([-50, self.HEIGHT + 50])
        else:
            return random.choice([-50, self.WIDTH + 50]), random.randint(0, self.HEIGHT)

    def draw_meteors(self):
        for meteor in self.meteors:
            self.sc.blit(meteor.image, [meteor.rect.x, meteor.rect.y])
            # pg.draw.rect(self.sc, (255, 0, 0), meteor.rect, 1)

    def check_collides(self):
        for meteor in self.meteors:
            collide = pg.sprite.collide_mask(meteor, self.player)
            if collide:
                self.meteors.remove(meteor)
                self.player.current_health -= 1
                if self.player.current_health == 0:
                    self.game_over = True
                for i in range(10):
                    self.particles.append([list(meteor.rect.center), [random.randint(0, 40) / 10 - 1, -2],
                                           random.randint(4, 6)])
                continue
            collide = pg.sprite.collide_mask(meteor, self.sun)
            if collide:
                self.meteors.remove(meteor)
                for i in range(10):
                    self.particles.append([list(meteor.rect.center), [random.randint(0, 40) / 10 - 1, -2],
                                           random.randint(4, 6)])
                self.money += random.choice(self.money_for_meteor)
                continue
            if self.shop_sys.items['moon']['bought'] and self.shop_sys.items['moon']['on']:
                collide = pg.sprite.collide_mask(meteor, self.moon)
                if collide:
                    self.meteors.remove(meteor)
                    for i in range(10):
                        self.particles.append([list(meteor.rect.center), [random.randint(0, 40) / 10 - 1, -2],
                                               random.randint(4, 6)])
                    self.money += random.choice(self.money_for_meteor)
                    continue

    def process(self):
        self.registry_set_key(HKEY_CURRENT_USER, r'Software\\SaveTheEarth', 'money', REG_SZ, f"{self.money}")
        self.registry_set_key(HKEY_CURRENT_USER, r'Software\\SaveTheEarth', 'items', REG_SZ, f"{self.shop_sys.items}")
        minute = str(self.timer // 60).zfill(2)
        seconds = str(self.timer % 60).zfill(2)
        self.timer_text = self.font_arial.render(f"{minute}:{seconds}", False, (255, 255, 255))
        self.money_text = self.font_arial.render(f"{self.money}$", False, (255, 255, 255))
        self.player.rotate()
        self.player.process()
        self.sun.move()
        pos = list(pg.mouse.get_pos())
        pos[1] += self.sun.rect.height
        self.fire_particle.pos = pos
        # self.sc.fill(0)
        self.fire_particle.update(self.sc, self.ticks)
        for meteor in self.meteors:
            meteor.move()
            if meteor.rect.x - 150 > self.WIDTH:
                self.meteors.remove(meteor)
            elif meteor.rect.x + 150 < 0:
                self.meteors.remove(meteor)
            elif meteor.rect.y - 150 > self.WIDTH:
                self.meteors.remove(meteor)
            elif meteor.rect.y + 150 < 0:
                self.meteors.remove(meteor)

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            particle[1][1] += 0.1
            if particle[2] <= 0:
                self.particles.remove(particle)

        if self.shop_sys.items['moon']['bought'] and self.shop_sys.items['moon']['on']:
            self.moon.rotate()

        self.check_collides()

    def run(self):
        dt = 0
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        if not self.game_over:
                            self.pause = not self.pause
                            if not self.pause:
                                pg.mouse.set_pos([self.sun.rect.x + self.sun.rect.width // 2,
                                                  self.sun.rect.y + self.sun.rect.height // 2])
                                pg.mouse.set_visible(False)
                            else:
                                pg.mouse.set_visible(True)
                        else:
                            self.game_over = False
                            self.restart_game()

                elif event.type == pg.KEYUP:
                    if event.key == pg.K_TAB:
                        self.tab_is_pressed = False
                        pg.mouse.set_pos([self.sun.rect.x + self.sun.rect.width // 2,
                                          self.sun.rect.y + self.sun.rect.height // 2])
                        pg.mouse.set_visible(False)

                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.tab_is_pressed:
                        self.shop()

                elif event.type == self.TIMER and not self.pause and not self.tab_is_pressed and not self.game_over:
                    self.timer += 1

                elif event.type == self.SPAWNAMETEOR and not self.pause and not self.tab_is_pressed and not self.game_over:
                    self.spawned_meteor += 1
                    if self.spawned_meteor % 10 == 0:
                        if self.spawn_meteor_time > 350:
                            self.spawn_meteor_time -= 50
                            pg.time.set_timer(self.SPAWNAMETEOR, self.spawn_meteor_time)  # 3 sec
                            self.money_for_meteor = range(self.money_for_meteor[0] + 1,
                                                          self.money_for_meteor[len(self.money_for_meteor) - 1] + 2)

                    for i in range(random.randint(1, 3)):
                        pos = self.get_random_pos()
                        self.meteors.add(Meteor(pos, [106, 80], 5, self.player.rect.center))

                self.manager.process_events(event)

            self.manager.update(dt / 1000.0)
            self.ticks = pg.time.get_ticks()

            key_pressed = pg.key.get_pressed()
            if key_pressed[pg.K_TAB]:
                pg.mouse.set_visible(True)
                self.tab_is_pressed = True

            self.draw_scene()
            self.manager.draw_ui(self.sc)

            if not self.tab_is_pressed and not self.pause and not self.game_over:
                self.process()

            pg.display.flip()
            dt = self.clock.tick(self.FPS)
            pg.display.set_caption(str(self.clock.get_fps()))

    def shop(self):
        dt = 0
        while True:
            self.registry_set_key(HKEY_CURRENT_USER, r'Software\\SaveTheEarth', 'money', REG_SZ, f"{self.money}")
            self.registry_set_key(HKEY_CURRENT_USER, r'Software\\SaveTheEarth', 'items', REG_SZ,
                                  f"{self.shop_sys.items}")
            self.money_text = self.font_arial.render(f"{self.money}$", False, (255, 255, 255))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        item = self.shop_sys.current_item
                        if item >= 0:
                            for i, keys_ in enumerate(self.shop_sys.items.keys()):
                                if i == item and not self.shop_sys.items[keys_]["bought"] \
                                        and self.shop_sys.items[keys_]["cost"] < self.money:
                                    self.shop_sys.items[keys_]["bought"] = True
                                    self.money -= self.shop_sys.items[keys_]["cost"]
                                elif i == item and self.shop_sys.items[keys_]["bought"]:
                                    self.shop_sys.items[keys_]["on"] = not self.shop_sys.items[keys_]["on"]

            self.manager.update(dt / 1000.0)
            self.sc.fill(0)

            self.shop_sys.render(self.money)

            self.sc.blit(self.money_text, [0, 0])

            pg.display.flip()
            dt = self.clock.tick(self.FPS)
            pg.display.set_caption(str(self.clock.get_fps()))


if __name__ == '__main__':
    app = Game()
    app.run()
