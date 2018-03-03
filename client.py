import pygame
from constants import *
import random as rd
import socket

class View():
    def __init__(self):
        self.establish_socket()
        print("Input player name.")
        self.name = input()
        self.send(self.name)

        pygame.init()

        self.control_dict = {'u': pygame.K_w,
                            'd': pygame.K_s,
                            'l': pygame.K_a,
                            'r': pygame.K_d,
                            's': pygame.K_RETURN}

        self.att = {}
        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])

        self.colors = {'r': (255, 0, 0),
            'g': (0, 255, 0),
            'b': (0, 0, 255),
            'y': (255, 255, 0)}
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
            self.port = 52801
            self.server.connect((SERVER_IP,self.port))
        except:
            raise ConnectionError("Could not connect to server.")

    def send(self, string):
        self.server.send(inputLetters.encode())

    def main(self):
        a = 0
        self.receive_map(self)
        update_thread = threading.Thread(target=self.update)
        update_thread.start()

    def read_keystrokes():
        while True:
            pygame.event.pump()
            events = pygame.event.get()
            pressed = pygame.get_pressed()
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
                    elif event.key == self.control_dict['s']:
                        self.do = 's'

            keys = [self.control_dict['u'],
                self.control_dict['d'],
                self.control_dict['l'],
                self.control_dict['r'],
                self.control_dict['s']]
            any_presses = 0
            for key in keys:
                if pressed[key]:
                    any_presses = 1
                    break
            if not any_presses:
                self.do = '0'
            self.send("%s:%s" % (self.name, self.do))
            

    def update(self):
        while True:
            self.screen.fill((0, 0, 0))
            self.draw_terrain(self.map)
            self.receive()
            pygame.display.flip()

    def receive_map(self):
        msg = server.recv(2048).decode()
        msg_split = msg.split(";")
        map_array = []
        for t in msg_split:
            map_array.append([int(a) for a in t])
        self.map = map_array

    def receive(self):
        msg = server.recv(2048).decode()
        msg_split = msg.split(";")
        for info in msg.split:
            key, data = info.split(":")
            data_split = data.split(",")
            self.draw_terrain(self.map)
            if key == "player":
                name = data_split[0]
                color = data_split[1]
                x = float(data_split[2])
                y = float(data_split[3])
                d = int(data_split[4])
                self.draw_player((x, y), d, name, color)
            elif key == "bullet":
                color = data_split[0]
                x = float(data_split[1])
                y = float(data_split[2])
                d = int(data_split[3])
                self.draw_bullet((x, y), color, d)

    def draw_bullet(self, pos, color, direction):
        r = int(BULLET_RAD*PIXELS_PER_UNIT)
        pos = (int(pos[0]*PIXELS_PER_UNIT), int(pos[1]*PIXELS_PER_UNIT))
        pygame.draw.circle(self.screen, self.colors[color], pos, r)

    def draw_terrain(self, terrain_list):
        for y, row in enumerate(terrain_list):
            for x, terr in enumerate(row):
                X, Y = x*PIXELS_PER_UNIT, y*PIXELS_PER_UNIT
                tile_x, tile_y = X - 0.5*TILE_WIDTH*PIXELS_PER_UNIT, Y - 0.5*TILE_WIDTH*PIXELS_PER_UNIT
                color = self.terrain_colors[terr]
                w, h = TILE_WIDTH * PIXELS_PER_UNIT, TILE_WIDTH * PIXELS_PER_UNIT
                tile_x += DRAW_OFFSET[0]
                tile_y += DRAW_OFFSET[1]
                pygame.draw.rect(self.screen, color, (tile_x, tile_y, w, h))

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


if __name__ == '__main__':
    a = View()
    a.main()
