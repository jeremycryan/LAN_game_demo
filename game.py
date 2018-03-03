from constants import SPAWN_RADIUS
from random import choice
from player import Player
from bullet import Bullet
from math import sqrt

class Game:
    def __init__(self, level="Basic"):
        ''' Reads a level from a file '''
        self.level = []
        self.players = []
        self.bullets = []
        with open("Levels/"+level+".txt", "r") as f:
            for line in f:
                self.level.append(list(line.strip()))

    def add_player(self, name, color):
        ''' Adds a player at a random open position '''
        space = []
        for y in range(len(self.level)):
            for x in range(len(self.level[y])):
                mindist = min([SPAWN_RADIUS]+list(map(lambda p:sqrt((p.x-x)**2+(p.y-y)**2),self.players)))
                if self.level[y][x]=='0' and mindist >= SPAWN_RADIUS:
                    space.append((x,y))
        if not len(space):
            print("Game is full")
            return
        self.players.append(Player(name, color, choice(space)))

    def update(self, dt):
        ''' Updates states of players and bullets '''
        for player in self.players:
            player.update(self.level, dt)
            if player.remove:
                self.players.remove(player)
            if player.shooting():
                self.bullets.append(Bullet(player.color, player.x, player.y, player.direction))
        for bullet in self.bullets:
            bullet.update(self.level, dt)
            bullet.collide(self.players)
            if bullet.remove:
                self.bullets.remove(bullet)

    def input(self, name, command):
        ''' Send a command to a player '''
        for player in self.players:
            if player.name == name:
                player.input(command)
                print("%s: %s" % (name, command))
                return

    def get_state(self):
        ''' Converts players and bullets to strings '''
        if not len(self.players):
            return ""
        return ';'.join(str(o) for o in self.players+self.bullets) + ';'

    def get_map(self):
        ''' Converts map to a string '''
        return ';'.join("".join(l) for l in self.level)

    def get_game_over(self):
        ''' Determines if all players are the same color '''
        if not len(self.players):
            return False
        c = self.players[0].color
        for player in self.players:
            if player.color!=c:
                return False
        return True

if __name__== "__main__":
    game = Game()
    game.add_player("Bob", "red")
    game.add_player("Joe", "green")
    game.update(1)
    game.input("Bob", 's')
    game.update(.01)
    game.update(.01)
    print(game.getState())
    print(game.getMap())
