from constants import BULLET_SPEED, PLAYER_WIDTH, BULLET_RAD, PLAYER_CODE, BULLET_CODE
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
        return BULLET_CODE+":"+self.color+","+str(round(self.x, 2))+","+ \
               str(round(self.y, 2))+","+str(self.direction)

def collide_walls(x, y, level):
    ''' Checks for collision with nearby walls '''
    open1 = level[round(y + BULLET_RAD/2)][round(x - BULLET_RAD/2)]=='0'
    open2 = level[round(y + BULLET_RAD/2)][round(x + BULLET_RAD/2)]=='0'
    open3 = level[round(y - BULLET_RAD/2)][round(x - BULLET_RAD/2)]=='0'
    open4 = level[round(y - BULLET_RAD/2)][round(x + BULLET_RAD/2)]=='0'
    return not(open1 and open2 and open3 and open4)
