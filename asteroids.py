from classes import *
from helpers import *
import math
import sys
import datetime
import random
import pygame
from network import Network


class MyGame(object):
    PLAYING, DYING, GAME_OVER, STARTING, WELCOME = range(5)
    REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT + 3)

    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        # Инициализируем окно
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Star wars on steroids')
        # Шрифты, звуки, картинки
        self.soundtrack = load_sound('soundtrack.wav')
        self.soundtrack.set_volume(.5)
        self.big_font = pygame.font.SysFont(None, 100)
        self.normal_font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 25)
        self.laserburst_sound = load_sound('laser.wav')
        self.gameover_text = self.big_font.render('Конец игры', True, (255, 255, 255))
        self.gameover_text2 = self.normal_font.render('Жмякни для новой игры', True, (255, 255, 255))
        self.lives_image = load_image('life.png')
        self.critical_distance = {"big": 100, "normal": 70, "small": 40}
        # Игровой таймер
        self.FPS = 30
        pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)
        self.fire_time = datetime.datetime.now()
        # Инициализруем вступительный экран
        self.state = MyGame.WELCOME
        self.welcome_logo = load_image('logo.png')
        self.welcome_text = self.big_font.render("Star Wars on steroids", True, (255, 255, 255))
        self.welcome_desc = self.normal_font.render("Жмякни по экрану", True, (255, 255, 255))

    def start(self):
        self.spaceship = Spaceship((self.width // 2, self.height // 2))
        self.friendship = Spaceship((self.width // 2, self.height // 2))
        self.net = Network()
        self.bursts = []
        self.soundtrack.play(-1, 0, 1000)
        self.state = MyGame.PLAYING

    def run(self):
        """Вечный цикл игры"""
        running = True
        while running:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                running = False
            elif event.type == MyGame.REFRESH:
                if self.state != MyGame.WELCOME:
                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_SPACE]:
                        new_time = datetime.datetime.now()
                        if new_time - self.fire_time > datetime.timedelta(seconds=0.5):
                            self.spaceship.fire()
                            self.laserburst_sound.play()
                            self.fire_time = new_time

                    if self.state == MyGame.PLAYING:
                        if keys[pygame.K_RIGHT]:
                            self.spaceship.angle -= 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_LEFT]:
                            self.spaceship.angle += 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_UP]:
                            self.spaceship.is_throttle_on = True
                            if self.spaceship.speed < 10:
                                self.spaceship.speed += 1
                        else:
                            if self.spaceship.speed > 0:
                                self.spaceship.speed -= 1
                            self.spaceship.is_throttle_on = False

                        if len(self.spaceship.active_bursts) > 0:
                            self.bursts_physics()

                        if len(self.hedgehoppers) > 0:
                            self.hedgehoppers_physics()

                        self.physics()

                self.draw()

            elif event.type == MyGame.START:
                pygame.time.set_timer(MyGame.START, 0)
                if self.lives < 1:
                    self.game_over()
                else:
                    self.hedgehoppers = []
                    for i in range(5):
                        self.make_hedgehopper()

                    self.start()

            elif event.type == MyGame.RESTART:
                pygame.time.set_timer(MyGame.RESTART, 0)
                self.state = MyGame.STARTING

            elif event.type == pygame.MOUSEBUTTONDOWN and (self.state == MyGame.STARTING
                                                           or self.state == MyGame.WELCOME):
                self.hedgehoppers = []
                self.start()
                for i in range(5):
                    self.make_hedgehopper()
                self.lives = 3
                self.score = 0
            else:
                pass

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.spaceship.position[0]) + "," + str(self.spaceship.position[1])
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0,0

    def make_hedgehopper(self, size="big", pos=None):
        """Создаем штурмовика размера size, по умолчанию большой"""
        margin = 200
        if pos == None:
            rand_x = random.randint(margin, self.width - margin)
            rand_y = random.randint(margin, self.height - margin)
            while distance((rand_x, rand_y), self.spaceship.position) < 400:
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)
            new_hedgehopper = Hedgehopper((rand_x, rand_y), size)
        else:
            new_hedgehopper = Hedgehopper(pos, size)

        self.hedgehoppers.append(new_hedgehopper)

    def game_over(self):
        """Игра окончена"""
        self.soundtrack.stop()
        self.state = MyGame.GAME_OVER
        pygame.time.set_timer(MyGame.RESTART, int(1000))

    def die(self):
        """Смерть"""
        self.soundtrack.stop()
        self.lives -= 1
        self.state = MyGame.DYING
        pygame.time.set_timer(MyGame.START, int(1000))

    def physics(self):
        """Движение и смерть за окном"""
        if self.state == MyGame.PLAYING:
            self.spaceship.move()

            # Отсылаем свои координаты, ловим второго игрока
            self.friendship.position[0], self.friendship.position[1] = self.parse_data(self.send_data())

            if self.spaceship.position[0] > 1280 or self.spaceship.position[0] < 0 \
                    or self.spaceship.position[1] > 720 or self.spaceship.position[1] < 0:
                self.die()

    def bursts_physics(self):
        """Убиение штурмовиков"""
        if len(self.spaceship.active_bursts) > 0:
            for burst in self.spaceship.active_bursts:
                burst.move()
                for hedgehopper in self.hedgehoppers:
                    if hedgehopper.size == "big":
                        if distance(burst.position, hedgehopper.position) < 70:
                            self.hedgehoppers.remove(hedgehopper)
                            if burst in self.spaceship.active_bursts:
                                self.spaceship.active_bursts.remove(burst)
                            self.make_hedgehopper("normal", (hedgehopper.position[0] + 10, hedgehopper.position[1]))
                            self.make_hedgehopper("normal", (hedgehopper.position[0] - 10, hedgehopper.position[1]))
                            self.score += 1
                    elif hedgehopper.size == "normal":
                        if distance(burst.position, hedgehopper.position) < 50:
                            self.hedgehoppers.remove(hedgehopper)
                            if burst in self.spaceship.active_bursts:
                                self.spaceship.active_bursts.remove(burst)
                            self.make_hedgehopper("small", (hedgehopper.position[0] + 10, hedgehopper.position[1]))
                            self.make_hedgehopper("small", (hedgehopper.position[0] - 10, hedgehopper.position[1]))
                            self.score += 1
                    else:
                        if distance(burst.position, hedgehopper.position) < 30:
                            self.hedgehoppers.remove(hedgehopper)
                            if burst in self.spaceship.active_bursts:
                                self.spaceship.active_bursts.remove(burst)
                            if len(self.hedgehoppers) < 10:
                                self.make_hedgehopper()
                            self.score += 1

    def hedgehoppers_physics(self):
        """Убийство игрока и выход за граница штурмовика"""
        if len(self.hedgehoppers) > 0:
            for hedgehopper in self.hedgehoppers:
                hedgehopper.move()

                if distance(hedgehopper.position, self.spaceship.position) < self.critical_distance[hedgehopper.size]:
                    self.die()
                elif distance(hedgehopper.position, (self.width / 2, self.height / 2)) > math.sqrt(
                        (self.width / 2) ** 2 + (self.height / 2) ** 2):
                    self.hedgehoppers.remove(hedgehopper)

                    if len(self.hedgehoppers) < 10:
                        self.make_hedgehopper(hedgehopper.size)

    def draw(self):
        """Тут все отрисовыватеся"""
        BackGround = Background('background.jpg', [0, 0])
        self.screen.blit(BackGround.image, BackGround.rect)
        if self.state != MyGame.WELCOME:
            self.spaceship.draw_on(self.screen)
            self.friendship.draw_on(self.screen)

            if len(self.spaceship.active_bursts) > 0:
                for burst in self.spaceship.active_bursts:
                    burst.draw_on(self.screen)

            if len(self.hedgehoppers) > 0:
                for hedgehopper in self.hedgehoppers:
                    hedgehopper.draw_on(self.screen)

            if len(self.hedgehoppers) < 10:
                self.make_hedgehopper()

            scores_text = self.small_font.render("Убито штурмовиков: " + str(self.score), True, (255, 255, 255))
            draw(scores_text, self.screen, (120, 100))

            if self.state == MyGame.GAME_OVER or self.state == MyGame.STARTING:
                draw(self.gameover_text, self.screen, (self.width // 2, self.height // 2))
                draw(self.gameover_text2, self.screen, (self.width // 2, self.height // 2 + 100))
            for i in range(self.lives):
                draw(self.lives_image, self.screen, (self.lives_image.get_width() * i + 60, 50))
        else:
            draw(self.welcome_logo, self.screen, (self.width // 2, 400))
            draw(self.welcome_text, self.screen, (self.width // 2, 50))
            draw(self.welcome_desc, self.screen, (self.width // 2, 100))

        pygame.display.flip()


MyGame().run()
pygame.quit()
sys.exit()
