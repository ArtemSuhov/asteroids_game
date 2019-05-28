import math
import os
import pygame

#Воспомогательные функции

def load_image(filename):
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()


def load_sound(filename):
    return pygame.mixer.Sound(os.path.join('music', filename))


def draw(this, on_this, position):
    rect = this.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    on_this.blit(this, rect)


def rotate(image, rect, angle):
        rotate_image = pygame.transform.rotate(image, angle)
        rotate_rect = rotate_image.get_rect(center=rect.center)
        return rotate_image,rotate_rect


def distance(p, q):
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)