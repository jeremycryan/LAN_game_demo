#------------------DISPLAY CONSTANTS----------------------------------

WINDOW_WIDTH = 950
WINDOW_HEIGHT = 950

PIXELS_PER_UNIT = 32
PROP_OFFSET = (1, 1)
DRAW_OFFSET = (PROP_OFFSET[0]*PIXELS_PER_UNIT,
    PROP_OFFSET[1]*PIXELS_PER_UNIT)

GUN_WIDTH = 0.2
GUN_LENGTH = 0.8
TILE_WIDTH = 0.95

NAME_OFFSET = 1.4

COLORS = ['c', 'm', 'r', 'g', 'b', 'y']*10

#------------------------NETWORK CONSTANTS----------------------------

SERVER_IP = "192.168.35.179"
PORT = 52801

#-----------------------PLAYER CONSTANTS------------------------------

SPEED = 3
COOLDOWN = 0.5

PLAYER_WIDTH = 0.7
BULLET_RAD = 0.2
BULLET_SPEED = 12

#--------------------------GAME CONSTANTS----------------------------

SPAWN_RADIUS = 3

#--------------------------PARSING-----------------------------------

PLAYER_CODE = 'P'
BULLET_CODE = 'B'
