import pygame
from constants import *
import random as rd
import socket
import threading
import numpy as np

class View():
    def __init__(self):
        self.establish_socket()
        print("Input player name.")
        self.name = input()
        self.send(self.name)
        self.sent = '0'
        self.do = '0'
        self.shoot = False

        pygame.init()

        self.control_dict = {'u': pygame.K_w,
                            'd': pygame.K_s,
                            'l': pygame.K_a,
                            'r': pygame.K_d,
                            's': pygame.K_RETURN}

        self.att = {}
        self.players = {}
        self.players[self.name]=[0, 0, 'd', 'y']
        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])

        self.colors = {'r': (200, 50, 20),
            'g': (0, 140, 40),
            'b': (90, 60, 210),
            'y': (220, 200, 0),
            'c': (0, 180, 220),
            'm': (220, 0, 200)}
        self.terrain_colors = {0: (55, 55, 55),
            1: (100, 100, 100)}

        self.max_name = 12

        self.name_font = pygame.font.SysFont("monospace", 20)
        self.example_map_1 = [[1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 0, 1],
                            [1, 0, 0, 1, 0, 0, 1],
                            [1, 0, 1, 1, 1, 0, 1],
                            [1, 0, 0, 1, 0, 0, 1],
                            [1, 0, 0, 0, 0, 0, 1],
                            [0, 1, 1, 1, 1, 1, 1]]

        self.map = []


    def establish_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.port = PORT
            self.server.connect((SERVER_IP,self.port))
        except:
            raise ConnectionError("Could not connect to server.")

    def cur_player(self):
        return self.players[self.name]

    def cur_pos(self):
        player = self.cur_player()
        cur_pos = np.asarray([float(player[0]), float(player[1])])
        return cur_pos

    def render_shadows(self):
        #   TODO implement this, and add it to rendering loop
        for row, row_list in enumerate(self.map):
            for col, cell in enumerate(row_list):
                cell_pos = np.asarray([col, row])
                self.shadows[row, col] = self.is_hidden(cell_pos)

    def send(self, string):
        self.server.send(string.encode())

    def main(self):
        a = 0
        print("Looking for map...")
        self.receive_map()
        update_thread = threading.Thread(target=self.update)
        update_thread.start()
        keypress_thread = threading.Thread(target=self.read_keystrokes)
        keypress_thread.start()

    def read_keystrokes(self):
        while True:
            #pygame.event.pump()
            events = pygame.event.get()
            pressed = pygame.key.get_pressed()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == self.control_dict['u']:
                        self.do = 'u'
                    elif event.key == self.control_dict['d']:
                        self.do = 'd'
                    elif event.key == self.control_dict['l']:
                        self.do = 'l'
                    elif event.key == self.control_dict['r']:
                        self.do = 'r'
                    if event.key == self.control_dict['s']:
                        self.shoot = True

            keys = [self.control_dict['u'],
                self.control_dict['d'],
                self.control_dict['l'],
                self.control_dict['r']]
            any_presses = 0
            if not pressed[self.control_dict['s']]:
                self.shoot = False
            for key in keys:
                if pressed[key]:
                    any_presses = 1
                    break
            if not any_presses:
                self.do = '0'
            if self.shoot:
                self.send("%s:%s" % (self.name, 's'))
                self.shoot = False
            if self.do != self.sent:
                self.send("%s:%s" % (self.name, self.do))
                self.sent = self.do

    def update(self):
        while True:
            self.render_shadows()
            self.receive()
            pygame.display.flip()

    def receive_map(self):
        msg = self.server.recv(2048).decode()
        msg_split = msg.split(";")
        map_array = []
        for t in msg_split:
            map_array.append([int(a) for a in t])
        self.map = np.asarray(map_array)
        self.shadows = np.zeros(self.map.shape)

    def receive(self):
        try:
            msg = self.server.recv(2048).decode()
            msg_split = msg.split(";")
            while '' in msg_split:
                msg_split.remove('')
            drawn = False
            players_drawn = []
            bullets_drawn = []
            for info in msg_split:
                key, data = info.split(":")
                data_split = data.split(",")
                if not drawn:
                    self.screen.fill((15, 15, 15))
                    self.draw_terrain(self.map)
                    drawn = True
                if key == "Player":
                    name = data_split[0]
                    color = data_split[1]
                    x = float(data_split[2])
                    y = float(data_split[3])
                    d = int(data_split[4])
                    if [name, x, y, d] in players_drawn:
                        continue
                    players_drawn.append([name, x, y, d])
                    self.players[name]=[x, y, d, color]
                    if not self.is_hidden(np.asarray([x, y])):
                        self.draw_player((x, y), d, name, color)
                elif key == "Bullet":
                    color = data_split[0]
                    x = float(data_split[1])
                    y = float(data_split[2])
                    d = int(data_split[3])
                    if [x, y, d] in bullets_drawn:
                        continue
                    bullets_drawn.append([x, y, d])
                    if not self.is_hidden(np.asarray([x, y])):
                        self.draw_bullet((x, y), color, d)
        except:
            print("Lost packet!")

    def draw_bullet(self, pos, color, direction):
        r = int(BULLET_RAD*PIXELS_PER_UNIT)
        pos = (int(pos[0]*PIXELS_PER_UNIT), int(pos[1]*PIXELS_PER_UNIT))
        pos = (pos[0] + DRAW_OFFSET[0], pos[1] + DRAW_OFFSET[1])
        pygame.draw.circle(self.screen, self.colors[color], pos, r)

    def draw_terrain(self, terrain_list):
        for y, row in enumerate(terrain_list):
            for x, terr in enumerate(row):
                if not self.shadows[y, x]:
                    X, Y = x*PIXELS_PER_UNIT, y*PIXELS_PER_UNIT
                    tile_x, tile_y = X - 0.5*TILE_WIDTH*PIXELS_PER_UNIT, Y - 0.5*TILE_WIDTH*PIXELS_PER_UNIT
                    color = self.terrain_colors[terr]
                    w, h = TILE_WIDTH * PIXELS_PER_UNIT, TILE_WIDTH * PIXELS_PER_UNIT
                    tile_x += DRAW_OFFSET[0]
                    tile_y += DRAW_OFFSET[1]
                    pygame.draw.rect(self.screen, color, (tile_x, tile_y, w, h))



    def is_hidden(self, obj_pos):
        if int(obj_pos[0])==obj_pos[0]:
            if self.map[int(obj_pos[1])][int(obj_pos[0])] == 1:
                return False
        start = self.cur_pos()
        diff_vec = np.asarray(obj_pos) - start
        dist = np.linalg.norm(diff_vec)
        if dist <= 1:
            return False
        if dist > 8:
            return True
        inc = diff_vec/dist/1.0
        inc_dist = 0
        while inc_dist + 1 < dist:
            start += inc
            inc_dist += np.linalg.norm(inc)
            x = int(round(start[0]))
            y = int(round(start[1]))
            if x == obj_pos[0] and y == obj_pos[1]:
                return False
            if self.map[y][x] == 1:
                return True
        return False

    def draw_player(self, pos, ori, name, color):
        pix_pos = (pos[0] * PIXELS_PER_UNIT, pos[1] * PIXELS_PER_UNIT)
        x, y = (pix_pos[0] - 0.5*PLAYER_WIDTH*PIXELS_PER_UNIT,
            pix_pos[1] - 0.5*PLAYER_WIDTH*PIXELS_PER_UNIT)
        w, h = PLAYER_WIDTH*PIXELS_PER_UNIT, PLAYER_WIDTH*PIXELS_PER_UNIT

        if ori in [270, 90]:
            gun_w = GUN_WIDTH*PIXELS_PER_UNIT
            gun_h = GUN_LENGTH*PIXELS_PER_UNIT
        elif ori in [180, 0]:
            gun_w = GUN_LENGTH*PIXELS_PER_UNIT
            gun_h = GUN_WIDTH*PIXELS_PER_UNIT
        else:
            raise ValueError("Orientation can only be [0, 90, 180, 270]")

        g_pos_dict = {270: (x+0.5*w - 0.5*gun_w, y+0.5*h - gun_h),
            90: (x+0.5*w - 0.5*gun_w, y+0.5*h),
            180: (x+0.5*w - gun_w, y+0.5*h - 0.5*gun_h),
            0: (x+0.5*w, y+0.5*h - 0.5*gun_h)}
        gun_x, gun_y = g_pos_dict[ori]


        text = self.name_font.render(name[:self.max_name], 1, (255, 255, 255))
        name_x = x - int(0.5*text.get_width()) + 0.5*PLAYER_WIDTH*PIXELS_PER_UNIT
        name_y = y - int(NAME_OFFSET*PIXELS_PER_UNIT) + PLAYER_WIDTH*PIXELS_PER_UNIT

        name_x += DRAW_OFFSET[0]
        name_y += DRAW_OFFSET[1]

        x += DRAW_OFFSET[0]
        y += DRAW_OFFSET[1]

        gun_x += DRAW_OFFSET[0]
        gun_y += DRAW_OFFSET[1]

        color = self.colors[color]
        self.screen.blit(text, (name_x, name_y))
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        pygame.draw.rect(self.screen, color, (gun_x, gun_y, gun_w, gun_h))

    def is_in_sight(self, viewer, object):
        viewer_pos = (round(viewer_pos[0]), round(viewer_pos[1]))

if __name__ == '__main__':
    a = View()
    a.main()
