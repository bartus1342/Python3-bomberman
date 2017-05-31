import numpy as np
import random
from PyQt5.QtGui import QPixmap, QImage, QColor
from PIL import Image

class Field():
    width = 16  # rozmiar tile w poziomie
    height = 16  # rozmiar tile w pionie
    def __init__(self):
        self.destructable = None
        self.sprite = None


class Border(Field):  # r,g,b = 0,0,0
    sprite = "Sprits//border.png"
    def __init__(self):
        super(Border, self).__init__()
        self.destructable = False

class Barrier(Field):  # 255,0,0
    sprite = "Sprits//barrier.png"
    def __init__(self):
        super(Barrier, self).__init__()
        self.destructable = False

class Grass(Field):  # 0, 255, 33
    sprite = "Sprits//grass.png"
    def __init__(self):
        super(Grass, self).__init__()
        self.destructable = False

class Brick(Field):  # 0,38,255
    sprite = "Sprits//brick.png"
    def __init__(self):
        super(Brick, self).__init__()
        self.destructable = True

class Map:
    type = {0: Grass, 1: Border, 2: Barrier, 3: Brick}

    def __init__(self):
        self.real_map = np.zeros((42, 42))
        self.tileWidth = 40  # ilosc tile w pionie
        self.tileHeight = 40  # ilosc tile w poziomie
        self.mapWidth = self.tileWidth * Field.width
        self.mapHeight = self.tileHeight * Field.height
        self.real_top = Field.height
        self.real_bottom = 2 * self.tileHeight + self.mapHeight
        self.real_left = Field.width
        self.real_right = 2 * self.tileWidth + self.mapWidth
        self.random_map()
        self.createMap()

    def random_map(self):
        self.map = Image.new("RGB", (42, 42))
        # grass
        self.map.paste((0, 255, 33), [0, 0, self.map.size[0], self.map.size[1]])
        # border
        for i in range(42):
            self.map.putpixel((i, 0), (0, 0, 0))
            self.map.putpixel((i, 41), (0, 0, 0))
            self.map.putpixel((0, i), (0, 0, 0))
            self.map.putpixel((41, i), (0, 0, 0))
        # brick
        for i in range(2, 20):
            for j in range(2, 20):
                if i % 2 == 0 and j % 2 == 0:
                    self.map.putpixel((i, j), (0, 38, 255))
        for i in range(20, 39):
            for j in range(2, 20):
                if i % 2 == 0 and j % 2 == 0:
                    self.map.putpixel((i + 1, j), (0, 38, 255))
        for i in range(2, 20):
            for j in range(20, 39):
                if i % 2 == 0 and j % 2 == 0:
                    self.map.putpixel((i, j + 1), (0, 38, 255))
        for i in range(20, 39):
            for j in range(20, 39):
                if i % 2 == 0 and j % 2 == 0:
                    self.map.putpixel((i + 1, j + 1), (0, 38, 255))
        # barrier
        chance = 0.15
        random.seed()
        for i in range(1, 41):
            for j in range(1, 41):
                liczba = random.random()
                if liczba <= chance:
                    self.map.putpixel((i, j), (255, 0, 0))

    def createMap(self):
        for i in range(self.tileWidth + 2):
            for j in range(self.tileWidth + 2):
                color = self.map.getpixel((i, j))
                if color == (0, 0, 0):
                    self.real_map[i][j] = 1
                elif color == (0, 255, 33):
                    self.real_map[i][j] = 0
                elif color == (255, 0, 0):
                    self.real_map[i][j] = 2
                elif color == (0, 38, 255):
                    self.real_map[i][j] = 3
                else:
                    print("Error")