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

        self.name_font = pygame.font.SysFont("monospace", int(20*PIXELS_PER_UNIT/32))
        self.example_map_1 = [[1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 0, 1],
                            [1, 0, 0, 1, 0, 0, 1],
                            [1, 0, 1, 1, 1, 0, 1],
                            [1, 0, 0, 1, 0, 0, 1],
                            [1, 0, 0, 0, 0, 0, 1],
                            [0, 1, 1, 1, 1, 1, 1]]

        self.map = []


    def establish_socket(self):
        """ Establishes connection with server socket, using constant IP
        and port number. """
        #TODO Determine these connection values dynamically somehow?

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.port = PORT
            self.server.connect((SERVER_IP,self.port))
        except:
            raise ConnectionError("Could not connect to server.")

    def cur_player(self):
        """ Returns the current player object. """
        return self.players[self.name]

    def cur_pos(self):
        """ Returns the position of the current player as a 1x2 numpy array. """
        player = self.cur_player()
        cur_pos = np.asarray([float(player[0]), float(player[1])])
        return cur_pos

    def render_shadows(self):
        """ Draws shadows over each cell the player can't see.
        Adds a 1 to each cell of self.shadows for each square a shadow should
        be drawn. """
        for row, row_list in enumerate(self.map):
            for col, cell in enumerate(row_list):
                cell_pos = np.asarray([col, row])
                self.shadows[row, col] = self.is_hidden(cell_pos)

    def send(self, string):
        """ Converts a message to UTF-8 and sends it to the server. """
        self.server.send(string.encode('UTF-8'))

    def main(self):
        """ Starts relevant threads for client side. """
        a = 0
        print("Looking for map...")
        self.receive_map()
        update_thread = threading.Thread(target=self.update)
        update_thread.start()
        keypress_thread = threading.Thread(target=self.read_keystrokes)
        keypress_thread.start()

    def read_keystrokes(self):
        """ Sends instructions to server based on keystrokes and controls in
        self.control_dict. Gives player commands in the following format:

        name:command

        where name is the name of the player, and command is a single-character
        string 'u' (move up), 'd' (down), 'l' (left), 'r' (right), 's' (shoot),
        or '0' (stop movement). """
        #   TODO generalize this thread enough that controls can be customized.
        #   TODO iterate through controls in a more efficient/elegant way.

        while True:
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
        """ Updates the game state based on socket messages, and draws to the
        screen. """
        while True:
            self.render_shadows()
            self.receive()
            pygame.display.flip()

    def receive_map(self):
        """ Waits for a message to be received from server, then creates
        a map variable based on the first message received.

        This map is an X by Y numpy array, with cells of integer value depending
        on what type of block is occupying that space in the map."""

        msg = self.server.recv(2048).decode('UTF-8')
        msg_split = msg.split(";")
        map_array = []
        for t in msg_split:
            map_array.append([int(a) for a in t])
        self.map = np.asarray(map_array)
        self.shadows = np.zeros(self.map.shape)

    def receive(self):
        """ Receives a gamestate message from the server and draws relevant
        items on the screen, based on what should be visible to the player. """

        #   TODO Make this section more robust to long packets to eliminate
        #   need for try/catch. Currently, it will occasionally crash if
        #   the data format is slightly wrong (for instance, if the buffer has
        #   filled and part of the message is cut off)
        try:
            msg = self.server.recv(4096).decode('UTF-8')
            if msg:
                drawn = False

                #   Parse the message
                msg_split = msg.split(";")
                while '' in msg_split:
                    msg_split.remove('')
                players_drawn = []
                bullets_drawn = []

                #   Draw each item in message
                for info in msg_split:
                    if len(info.split(":")) == 2:
                        key, data = info.split(":")
                        data_split = data.split(",")
                    else:
                        continue

                    #   Draw map if it hasn't been drawn yet this function call.
                    if not drawn:
                        self.screen.fill((15, 15, 15))
                        self.draw_terrain(self.map)
                        drawn = True

                    #   Draw each player, if it isn't hidden.
                    if key == PLAYER_CODE:
                        name = data_split[0]
                        if name in players_drawn:
                            continue
                        color = data_split[1]
                        x = float(data_split[2])
                        y = float(data_split[3])
                        d = int(data_split[4])
                        players_drawn.append(name)
                        self.players[name]=[x, y, d, color]
                        if not self.is_hidden(np.asarray([x, y])):
                            self.draw_player((x, y), d, name, color)

                    #   Draw each bullet, if it isn't hidden.
                    elif key == BULLET_CODE:
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
            print("Lost packet.")

    def draw_bullet(self, pos, color, direction):
        """ Draws a bullet to the screen at the given position. """
        r = int(BULLET_RAD*PIXELS_PER_UNIT)
        pos = (int(pos[0]*PIXELS_PER_UNIT), int(pos[1]*PIXELS_PER_UNIT))
        pos = (pos[0] + DRAW_OFFSET[0], pos[1] + DRAW_OFFSET[1])
        pygame.draw.circle(self.screen, self.colors[color], pos, r)

    def draw_terrain(self, terrain_list):
        """ Draws the terrain in the map. """
        #   TODO Use actual sprites, or at least something more interesting
        #   than gray squares.
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
        """ Determines whether an object is hidden, based on the map object
        and the position of the current player.

        Returns True if object is not visible, and False if it is visible. """
        #   TODO make this more computationally efficient

        #   Don't hide obstacle squares on the map.
        if int(obj_pos[0])==obj_pos[0]:
            if self.map[int(obj_pos[1])][int(obj_pos[0])] == 1:
                return False

        start = self.cur_pos()
        diff_vec = np.asarray(obj_pos) - start
        dist = np.linalg.norm(diff_vec)

        #   Show the object if you are right on top of it, even if algorithm
        #   thinks it should be hidden.
        if dist <= 1:
            return False

        #   Hide objects that are too far away.
        if dist > 8:
            return True
        inc = diff_vec/dist/1.0
        inc_dist = 0

        #   Increment along vector between player and object, determining
        #   whether there is an obstacle between.
        while inc_dist + 1 < dist:
            start += inc
            inc_dist += np.linalg.norm(inc)
            x = int(round(start[0]))
            y = int(round(start[1]))
            if x == obj_pos[0] and y == obj_pos[1]:
                return False

            #   If opaque map block is found, object is hidden.
            #   TODO generalize this to recognize other opaque blocks.
            if self.map[y][x] == 1:
                return True
        return False

    def draw_player(self, pos, ori, name, color):
        """ Draws a player on the screen at the given position.

        pos: tuple (x,y)
        ori: int anticlockwise angle from positive x axis, degrees. One of
            [0, 90, 180, 270]
        name: string for the player's name, to be drawn above head
        color: tuple (r, g, b), with values 0-255 """

        pix_pos = (pos[0] * PIXELS_PER_UNIT, pos[1] * PIXELS_PER_UNIT)
        x, y = (pix_pos[0] - 0.5*PLAYER_WIDTH*PIXELS_PER_UNIT,
            pix_pos[1] - 0.5*PLAYER_WIDTH*PIXELS_PER_UNIT)
        w, h = PLAYER_WIDTH*PIXELS_PER_UNIT, PLAYER_WIDTH*PIXELS_PER_UNIT

        #   Determine cannon size based on orientation.
        #   TODO use an actual sprite
        if ori in [270, 90]:
            gun_w = GUN_WIDTH*PIXELS_PER_UNIT
            gun_h = GUN_LENGTH*PIXELS_PER_UNIT
        elif ori in [180, 0]:
            gun_w = GUN_LENGTH*PIXELS_PER_UNIT
            gun_h = GUN_WIDTH*PIXELS_PER_UNIT
        else:
            raise ValueError("Orientation can only be [0, 90, 180, 270]")

        #   TODO generalize this, use a sprite, or otherwise make this
        #   dictionary less nasty.
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
