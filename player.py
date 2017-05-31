from map import Map, Field
from PyQt5.QtGui import QPixmap
import random
import numpy as np
import math

class Bomberman:
    def __init__(self): # uwzglednienie krawedzi mapy
        self.name = None
        self.sprite = None
        self.size_x = Field.width
        self.size_y = Field.height
        self.xpos_left = 0
        self.xpos_right = self.size_x
        self.ypos_top = 0
        self.ypos_bottom = self.size_y

    def update(self, mapa, parent):
        if parent.W_key:
            self.move_up(mapa)
        if parent.S_key:
            self.move_down(mapa)
        if parent.A_key:
            self.move_left(mapa)
        if parent.D_key:
            self.move_right(mapa)

    def move_down(self, mapa):
        self.ypos_bottom += 1
        if self.check_tile(mapa):
            self.ypos_top += 1
        else:
            count = 0
            while True:
                self.ypos_bottom -= 1
                count += 1
                if self.check_diff(mapa, 1):  # 1->dol
                    break
            self.ypos_top += 1
            self.ypos_top -= count



    def move_up(self, mapa):
        self.ypos_top -= 1
        if self.check_tile(mapa):
            self.ypos_bottom -= 1
        else:
            count = 0
            while True:
                self.ypos_top += 1
                count += 1
                if self.check_diff(mapa, 0):  # 0->gora
                    break
            self.ypos_bottom -= 1
            self.ypos_bottom += count

    def move_left(self, mapa):
        self.xpos_left -= 1
        if self.check_tile(mapa):
            self.xpos_right -= 1
        else:
            count = 0
            while True:
                self.xpos_left += 1
                count += 1
                if self.check_diff(mapa, 2):  # 2->lewo
                    break
            self.xpos_right -= 1
            self.xpos_right += count

    def move_right(self, mapa):
        self.xpos_right += 1
        if self.check_tile(mapa):
            self.xpos_left += 1
        else:
            count = 0
            while True:
                self.xpos_right -= 1
                count += 1
                if self.check_diff(mapa, 3):  # 3->prawo
                    break
            self.xpos_left += 1
            self.xpos_left -= count

    def print_pos(self, index):
        print("Gracz {4}: {0}-{1} : x, {2}-{3} : y".format(self.xpos_left, self.xpos_right, self.ypos_top, self.ypos_bottom, index+1))

    def check_tile(self, map):
        corner1 = (self.xpos_left, self.ypos_top)
        corner2 = (self.xpos_right, self.ypos_top)
        corner3 = (self.xpos_left, self.ypos_bottom)
        corner4 = (self.xpos_right, self.ypos_bottom)
        corners = [corner1, corner2, corner3, corner4]
        for i in range(len(corners)):
            x = int(corners[i][0] / 16)
            y = int(corners[i][1] / 16)
            if map.real_map[x][y] == 1 or map.real_map[x][y] == 2 or map.real_map[x][y] == 3:
                return False
        return True

    def check_diff(self, map, dir):
        if dir == 0:
            corner1 = (self.xpos_left, self.ypos_top)
            corner2 = (self.xpos_right, self.ypos_top)
        elif dir == 1:
            corner1 = (self.xpos_left, self.ypos_bottom)
            corner2 = (self.xpos_right, self.ypos_bottom)
        elif dir == 2:
            corner1 = (self.xpos_left, self.ypos_top)
            corner2 = (self.xpos_left, self.ypos_bottom)
        elif dir == 3:
            corner1 = (self.xpos_right, self.ypos_top)
            corner2 = (self.xpos_right, self.ypos_bottom)
        else:
            corner1 = None
            corner2 = None
        corners = [corner1, corner2]
        for i in range(len(corners)):
            x = int(corners[i][0] / 16)
            y = int(corners[i][1] / 16)
            if map.real_map[x][y] == 1 or map.real_map[x][y] == 2 or map.real_map[x][y] == 3:
                return False
        return True


class Gamer(Bomberman):
    sprite = "Sprits//player.png"
    def __init__(self, pos_start=(0, 0)):
        super(Gamer, self).__init__()
        self.sprite = "Sprits//player.png"
        self.xpos_left = pos_start[0]
        self.ypos_top = pos_start[1]
        self.xpos_right = pos_start[0] + self.size_x - 1
        self.ypos_bottom = pos_start[1] + self.size_y - 1
        self.blocked = [False, False, False, False]
        self.wait = []

    def ai_move(self, mapa, parent):
        opp_index, opp_odl_x, opp_odl_y = self.near_opp(parent.players)
        bomb_index, bomb_odl_x, bomb_odl_y = self.near_bomb(parent.obiekty)
        blocks_left, blocks_right, blocks_top, blocks_bottom = self.near_tiles(mapa)
        bomb = None
        ##############################################################################
        if self.wait:
            print("wait")
        else:
            if 3 * Field.width > bomb_odl_x >= 0 and (abs(bomb_odl_y) <= Field.height/2):  # czy bomba w zasiegu po lewej i po y
                if blocks_right[0] == 0 and blocks_right[1] == 0:  # czy wolne po prawej
                    self.move_right(mapa)
                elif (blocks_right[0] == 2 or blocks_right[1] == 2) or (blocks_right[0] == 3 or blocks_right[1] == 3) or (blocks_right[0] == 1 or blocks_right[1] == 1): # czy przeszkoda po prawej
                    if not self.blocked[0]:
                        self.move_up(mapa)
                    elif not self.blocked[1]:
                        self.move_down(mapa)
            elif -3 * Field.width < bomb_odl_x <= 0 and (abs(bomb_odl_y) <= Field.height/2): # czy bomba w zasiegu po prawej i po y
                if blocks_left[0] == 0 and blocks_left[1] == 0:  # czy wolne po prawej
                    self.move_right(mapa)
                elif (blocks_left[0] == 2 or blocks_left[1] == 2) or (blocks_left[0] == 3 or blocks_left[1] == 3) or (blocks_left[0] == 1 or blocks_left[1] == 1):
                    if not self.blocked[0]:
                        self.move_up(mapa)
                    elif not self.blocked[1]:
                        self.move_down(mapa)
            elif 3 * Field.height > bomb_odl_y >= 0 and (abs(bomb_odl_x) <= Field.width/2): # czy bomba w zasiegu na gorze i po x
                if blocks_bottom[0] == 0 and blocks_bottom[1] == 0:  # czy wolne po prawej
                    self.move_down(mapa)
                elif (blocks_bottom[0] == 2 or blocks_bottom[1] == 2) or (blocks_bottom[0] == 3 or blocks_bottom[1] == 3) or (blocks_bottom[0] == 1 or blocks_bottom[1] == 1):
                    if not self.blocked[2]:
                        self.move_left(mapa)
                    elif not self.blocked[3]:
                        self.move_right(mapa)
            elif -3 * Field.height < bomb_odl_y <= 0 and (abs(bomb_odl_x) <= Field.width / 2):  # czy bomba w zasiegu na dole i po x
                if blocks_top[0] == 0 and blocks_top[1] == 0:  # czy wolne po prawej
                    self.move_up(mapa)
                elif (blocks_top[0] == 2 or blocks_top[1] == 2) or (blocks_top[0] == 3 or blocks_top[1] == 3) or (blocks_top[0] == 1 or blocks_top[1] == 1):
                    if not self.blocked[2]:
                        self.move_left(mapa)
                    elif not self.blocked[3]:
                        self.move_right(mapa)
            #############################################################################
            elif opp_odl_x < 0:  # gdzieś po prawej
                if blocks_right[0] == 0 and blocks_right[1] == 0:
                    self.move_right(mapa)
                elif blocks_right[0] == 0 and (blocks_right[1] == 3 or blocks_right[1] == 2):
                    self.move_up(mapa)
                elif (blocks_right[0] == 3 or blocks_right[1] == 2) and blocks_right[1] == 0:
                    self.move_down(mapa)
                elif blocks_right[0] == 3 and blocks_right[1] == 3:  # jeśli jest blokada zniszczalna
                    bomb = [self.xpos_left, self.ypos_top]
                elif blocks_right[0] == 2 and blocks_right[1] == 2:
                    if blocks_bottom[0] == 3 and blocks_bottom[1] == 3:
                        bomb = [self.xpos_left, self.ypos_top]
                    self.blocked[3] = True
                    self.move_down(mapa)
            elif opp_odl_x > 0:
                self.move_left(mapa)
        return bomb

    def near_tiles(self, mapa):
        # lewo
        corner1 = [self.xpos_left - 1, self.ypos_top]
        corner2 = [self.xpos_left - 1, self.ypos_bottom]
        if corner1[0] < 0:
            corner1[0] = 0
        if corner2[0] < 0:
            corner2[0] = 0
        corner1 = [int(corner1[0] / 16), int(corner1[1] / 16)]
        corner2 = [int(corner2[0] / 16), int(corner2[1] / 16)]
        left_up = mapa.real_map[corner1[0]][corner1[1]]
        left_down = mapa.real_map[corner2[0]][corner2[1]]
        left = [left_up, left_down]
        # prawo
        corner1 = [self.xpos_right + 1, self.ypos_top]
        corner2 = [self.xpos_right + 1, self.ypos_bottom]
        if corner1[0] > Field.width * 42:
            corner1[0] = Field.width * 42
        if corner2[0] > Field.width * 42:
            corner2[0] = Field.width * 42
        corner1 = [int(corner1[0] / 16), int(corner1[1] / 16)]
        corner2 = [int(corner2[0] / 16), int(corner2[1] / 16)]
        right_up = mapa.real_map[corner1[0]][corner1[1]]
        right_down = mapa.real_map[corner2[0]][corner2[1]]
        right = [right_up, right_down]
        # gora
        corner1 = [self.xpos_left, self.ypos_top - 1]
        corner2 = [self.xpos_right, self.ypos_top - 1]
        if corner1[1] < 0:
            corner1[1] = 0
        if corner2[1] < 0:
            corner2[1] = 0
        corner1 = [int(corner1[0] / 16), int(corner1[1] / 16)]
        corner2 = [int(corner2[0] / 16), int(corner2[1] / 16)]
        top_left = mapa.real_map[corner1[0]][corner1[1]]
        top_right = mapa.real_map[corner2[0]][corner2[1]]
        top = [top_left, top_right]
        # dol
        corner1 = [self.xpos_left, self.ypos_bottom + 1]
        corner2 = [self.xpos_right, self.ypos_bottom + 1]
        if corner1[1] > Field.width * 42:
            corner1[1] = Field.width * 42
        if corner2[1] > Field.width * 42:
            corner2[1] = Field.width * 42
        corner1 = [int(corner1[0] / 16), int(corner1[1] / 16)]
        corner2 = [int(corner2[0] / 16), int(corner2[1] / 16)]
        bottom_left = mapa.real_map[corner1[0]][corner1[1]]
        bottom_right = mapa.real_map[corner2[0]][corner2[1]]
        bottom = [bottom_left, bottom_right]
        return left, right, top, bottom

    def near_opp(self, list):
        odlx = 0
        odly = 0
        min = -1
        wek_min = 1000
        for index in range(1, len(list)):
            if len(list) == 0:
                break
            wek = math.sqrt((self.xpos_left-list[index].xpos_left)**2 + (self.ypos_top-list[index].ypos_top)**2)
            if wek < wek_min:
                min = index
                wek_min = wek
                odlx = self.xpos_left-list[index].xpos_left
                odly = self.ypos_top-list[index].ypos_top
        return min, odlx, odly


    def near_bomb(self, list):
        odlx = 0
        odly = 0
        min = -1
        wek_min = 1000
        if not list:
            return -1, 1000, 1000
        for index in range(0, len(list)):
            wek = math.sqrt((self.xpos_left - list[index].posx_left) ** 2 + (self.ypos_top - list[index].posy_top) ** 2)
            if wek < wek_min:
                min = index
                wek_min = wek
                odlx = self.xpos_left - list[index].posx_left
                odly = self.ypos_top - list[index].posy_top
        return min, odlx, odly


class Enemy(Bomberman):
    sprite = "Sprits//enemy.png"
    def __init__(self, pos_start=(0, 0)):
        super(Enemy, self).__init__()
        self.sprite = "Sprits//enemy.png"
        self.xpos_left = pos_start[0]
        self.ypos_top = pos_start[1]
        self.xpos_right = pos_start[0] + self.size_x - 1
        self.ypos_bottom = pos_start[1] + self.size_y - 1