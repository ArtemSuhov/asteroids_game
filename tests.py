import unittest
import sys
import os
import datetime
import random
import pygame
from classes import *

class TestOfSpaceShip(unittest.TestCase):

  def test_creation_is_right(self):
      self.spaceship = Spaceship((150, 150))
      self.assertEqual(self.spaceship.position, (150, 150))

if __name__ == '__main__':
    unittest.main()