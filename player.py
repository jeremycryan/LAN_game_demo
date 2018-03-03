#from constants import SPEED, COOLDOWN
SPEED = 3
COOLDOWN = 0.5
from math import sin, cos, radians, floor, ceil

class Player:
    def __init__(self, name, color, pos, direction = 270):
        self.name = name
        self.color = color
        self.x = pos[0]
        self.y = pos[1]
        self.direction = direction
        self.move = False
        self.remove = False
        self.shoot = False
        self.cooldown = 0

    def update(self, level, dt):
        ''' Updates player position by one timestep '''
        if self.move:
            x2 = self.x + dt*SPEED*cos(radians(self.direction))
            y2 = self.y + dt*SPEED*sin(radians(self.direction))
            if not collide_walls(x2, y2, level):
                self.x = x2
                self.y = y2
        self.cooldown = max(0, self.cooldown-dt)

    def shooting(self):
        ''' Returns true if the player has fired a shot '''
        if self.shoot and not self.cooldown:
            self.shoot = False
            self.cooldown = COOLDOWN
            return True
        return False

    def input(self, command):
        ''' Parses an array of user input commands '''
        if command == 'r':
            self.direction = 0
            self.move = True
        elif command == 'd':
            self.direction = 90
            self.move = True
        elif command == 'l':
            self.direction = 180
            self.move = True
        elif command == 'u':
            self.direction = 270
            self.move = True
        elif command == 's':
            self.shoot = True
        elif command == '0':
            self.move = False
        elif command == 'x':
            self.remove = True

    def hit(self, color):
        ''' Callback when player is hit by a bullet '''
        if self.color!=color:
            self.color = color

    def __repr__(self):
        ''' Prints a more useful description of the object '''
        return "Player:"+self.name+","+self.color+","+str(self.x)+","+ \
               str(self.y)+","+str(self.direction)

def collide_walls(x, y, level):
    ''' Checks for collision with nearby walls '''
    open1 = level[floor(y)][floor(x)]=='0'
    open2 = level[ceil(y)][floor(x)]=='0'
    open3 = level[floor(y)][ceil(x)]=='0'
    open4 = level[ceil(y)][ceil(x)]=='0'
    return not(open1 and open2 and open3 and open4)
