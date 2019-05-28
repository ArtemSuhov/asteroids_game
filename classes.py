from helpers import *
import math
import sys
import os
import datetime
import random
import pygame


# Классы игрового объекта


class GameObject(object):
    def __init__(self, position, image, speed=0):
        self.image = image
        self.position = list(position[:])
        self.speed = speed

    def draw_on(self, screen):
        draw(self.image, screen, self.position)

    def size(self):
        return max(self.image.get_height(), self.image.get_width())

    def radius(self):
        return self.image.get_width() / 2


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Spaceship(GameObject):
    def __init__(self, position):
        super(Spaceship, self).__init__(position, load_image('spaceship-2.png'))
        self.image_on = load_image('spaceship-1.png')
        self.direction = [0, -1]
        self.is_throttle_on = False
        self.angle = 0
        self.active_bursts = []

    def draw_on(self, screen):
        if self.is_throttle_on:
            new_image, rect = rotate(self.image_on, self.image_on.get_rect(), self.angle)
        else:
            new_image, rect = rotate(self.image, self.image.get_rect(), self.angle)

        draw(new_image, screen, self.position)

    def fire(self):
        fireSpawns = [0, 0, 0, 0]
        fireSpawns[0] = math.sin(-math.radians(self.angle) - 1.2) * (self.image.get_width() // 2)
        fireSpawns[1] = -math.cos(math.radians(self.angle) + 1.2) * (self.image.get_height() // 2)
        fireSpawns[2] = -math.sin(-math.radians(self.angle) - 1.94) * (self.image.get_width() // 2)
        fireSpawns[3] = math.cos(math.radians(self.angle) + 1.94) * (self.image.get_height() // 2)

        new_laserburst = Laserburst((self.position[0] + fireSpawns[0], self.position[1] + fireSpawns[1]), self.angle)
        new_laserburst2 = Laserburst((self.position[0] + fireSpawns[2], self.position[1] + fireSpawns[3]), self.angle)
        self.active_bursts.append(new_laserburst)
        self.active_bursts.append(new_laserburst2)

    def move(self):
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed


class Hedgehopper(GameObject):
    def __init__(self, position, size, speed=4):
        if size in {"big", "normal", "small"}:
            str_filename = "hedgehopper_" + str(size) + ".png"
            super(Hedgehopper, self).__init__(position, load_image(str_filename))
            self.size = size
        else:
            return None

        self.position = list(position)
        self.speed = speed

        if bool(random.getrandbits(1)):
            rand_x = random.random() * -1
        else:
            rand_x = random.random()

        if bool(random.getrandbits(1)):
            rand_y = random.random() * -1
        else:
            rand_y = random.random()

        self.direction = [rand_x, rand_y]

    def move(self):
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed


class Laserburst(GameObject):
    def __init__(self, position, angle, speed=20):
        super(Laserburst, self).__init__(position, load_image('point.png'))
        self.angle = angle
        self.direction = [0, 0]
        self.speed = speed

    def move(self):
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed
