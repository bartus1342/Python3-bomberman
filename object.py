from map import Map, Field
from player import Gamer
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import threading
import time


class Bomb:
    sprite = "Sprits//bomb.png"
    def __init__(self, parent, x, y):
        self.parent = parent
        self.sprite = "Sprits//bomb.png"
        self.explodeTime = 3000  # sekundy
        self.start_bomb = int(round(time.time() * 1000))
        self.explode = False
        self.range = 2  # 1-5 pol
        self.posx_left = x  # lewy player
        self.posy_top = y  # top player
        self.posx_right = x + Field.width - 1
        self.posy_bottom = y + Field.height - 1


    def boom(self, map, player):
        x_range = [self.posx_left - self.range * Field.width, self.posx_right + self.range * Field.width]
        y_range = [self.posy_top - self.range * Field.height, self.posy_bottom + self.range * Field.height]
        if x_range[0] <= map.real_left:
            x_range[0] = map.real_left
        if x_range[1] >= map.real_right - 1:
            x_range[1] = map.real_right - 1
        if y_range[0] <= map.real_top:
            y_range[0] = map.real_top
        if y_range[1] >= map.real_bottom - 1:
            y_range[1] = map.real_bottom - 1
        ###########################################################################
        kaput = []
        for i in range(len(player)):
            if (player[i].xpos_left >= x_range[0] and player[i].ypos_top >= self.posy_top and player[i].xpos_right <= x_range[1] and
                        player[i].ypos_bottom <= self.posy_bottom) or (player[i].xpos_left >= self.posx_left and player[i].xpos_right
                        <= self.posx_right and player[i].ypos_top >= y_range[0] and player[i].ypos_bottom <= y_range[1]):
                kaput.append(i)
        destroyed = self.destroy_tile(map, x_range, y_range)
        return kaput, destroyed

    def destroy_tile(self, map, rangex, rangey):
        blocked = [False, False, False, False]
        destroyed = []
        x_part = (rangex[1] - rangex[0]) / (self.range * 2)
        y_part = (rangey[1] - rangey[0]) / (self.range * 2)
        center = ((self.posx_left+self.posx_right)/2, (self.posy_top+self.posy_bottom)/2)
        for i in range(0, self.range): # sprawdz po x
            left_tile = center[0] - (i + 1) * x_part
            right_tile = center[0] + (i + 1) * x_part
            x1, y1 = int(left_tile / 16), int(center[1] / 16)
            x2, y2 = int(right_tile / 16), int(center[1] / 16)
            if x1 < 0:
                x1 = 0
            if x2 > 41:
                x2 = 41
            if map.real_map[x1][y1] == 2:
                blocked[2] = True
            elif map.real_map[x1][y1] == 3 and not blocked[2]:
                map.real_map[x1][y1] = 0
                destroyed.append((x1, y1, 0))
            elif map.real_map[x2][y2] == 2:
                blocked[3] = True
            elif map.real_map[x2][y2] == 3 and not blocked[3]:
                map.real_map[x2][y2] = 0
                destroyed.append((x2, y2, 0))
        for i in range(0, self.range): # sprawdz po y
            up_tile = center[1] - (i + 1) * y_part
            down_tile = center[1] + (i + 1) * y_part
            x1, y1 = int(center[0] / 16), int(up_tile / 16)
            x2, y2 = int(center[0] / 16), int(down_tile / 16)
            if y1 < 0:
                y1 = 0
            if y2 > 41:
                y2 = 41
            if map.real_map[x1][y1] == 2:
                blocked[0] = True
            elif map.real_map[x1][y1] == 3 and not blocked[0]:
                map.real_map[x1][y1] = 0
                destroyed.append((x1, y1, 0))
            if map.real_map[x2][y2] == 2:
                blocked[1] = True
            elif map.real_map[x2][y2] == 3 and not blocked[1]:
                map.real_map[x2][y2] = 0
                destroyed.append((x2, y2, 0))
        return destroyed

    def update(self, mapa, players, czas):
         if czas - self.start_bomb >= self.explodeTime:
            self.explode = True
            print("boom w {0}-{1}".format(self.posx_left, self.posy_top))
            kaput, destroyed = self.boom(mapa, players)
            self.parent.odrysuj.append(destroyed)
            if not len(kaput) == 0:
                for j in range(len(kaput)):
                    if kaput[j] == 0:
                        print("Zginales. Koniec gry")
                        self.parent.players.pop(0)
                        return 1
                    else:
                        print("Gracz {} zginal.".format(kaput[j] + 1))
                        self.parent.players.pop(kaput[j])
            return 0
         return -1