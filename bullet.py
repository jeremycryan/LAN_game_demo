# from constants import BULLET_SPEED, PLAYER_WIDTH, BULLET_RAD
BULLET_SPEED = 5
PLAYER_WIDTH = 0.7
BULLET_RAD = 0.2
from math import cos, sin, radians, floor, ceil

class Bullet:
    def __init__(self, color, x, y, direction):
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
        self.x += (PLAYER_WIDTH/2+BULLET_RAD)*cos(radians(self.direction))
        self.y += (PLAYER_WIDTH/2+BULLET_RAD)*sin(radians(self.direction))
        self.remove = False

    def update(self, level, dt):
        ''' Updates bullet position by one timestep '''
        self.x += dt*BULLET_SPEED*cos(radians(self.direction))
        self.y += dt*BULLET_SPEED*sin(radians(self.direction))
        if collide_walls(self.x, self.y, level):
            self.remove = True

    def collide(self, players):
        ''' Checks for collisions with players '''
        for player in players:
            if abs(player.x-self.x) < PLAYER_WIDTH/2+BULLET_RAD/2:
                if abs(player.y-self.y) < PLAYER_WIDTH/2+BULLET_RAD/2:
                    self.remove = True
                    player.hit(self.color)
                    return

    def __repr__(self):
        ''' Prints a more useful description of the object '''
        return "Bullet:"+self.color+","+str(self.x)+","+ \
               str(self.y)+","+str(self.direction)

def collide_walls(x, y, level):
    ''' Checks for collision with nearby walls '''
    open1 = level[floor(y)][floor(x)]=='0'
    open2 = level[ceil(y)][floor(x)]=='0'
    open3 = level[floor(y)][ceil(x)]=='0'
    open4 = level[ceil(y)][ceil(x)]=='0'
    return not (open1 and open2 and open3 and open4)