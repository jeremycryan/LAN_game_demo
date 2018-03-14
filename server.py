import socket
import sys
import threading
from game import Game
import time
from constants import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP_address = SERVER_IP
#PORT = 52801

server.bind((IP_address,PORT))

#   TODO confirm this is a reasonable value for this parameter.
server.listen(2000)

#   TODO make a way to load whatever level is wanted, perhaps by a
#   host player.
game = Game(level='Cells')


clients = []

def clientThread(conn, addr):
    """ Listens to player, and sends them map data. """
    print("Connection started")
    print(addr)
    message = conn.recv(2048)
    print(message.decode('UTF-8'))
    game.add_player(strip_special(message.decode('UTF-8')), COLORS.pop())
    conn.send(game.get_map().encode('UTF-8'))
    time.sleep(2)
    clients.append(conn)

    while True:
        try:
            message = conn.recv(2048)
            if message:
                game.input(*message.decode('UTF-8').split(":"))
        except:
          continue

def strip_special(string):
    return string.replace(":", "").replace(";", "").replace(",", "")

def updatePlayers():
    """ Updates each player each time step. This essentially gives the
    player a game state object, which acts as a single frame. """

    state = None
    while True:
        new_state = game.get_state()
        if new_state != state:
            state = new_state
            for client in clients:
                try:
                    client.send(new_state.encode('UTF-8'))
                #   Remove the client if the message is not received.
                except:
                    client.close()
                    if client in clients:
                        clients.remove(client)
        #   TODO determine this delay amount based on whether the message
        #   has been received, or the player is otherwise able to receive
        #   the message.
        time.sleep(0.05)

def gameThread():
    """ Updates the game object every time step. """
    t = time.time()
    while True:
        new_t = time.time()
        dt = new_t - t
        t = new_t
        game.update(dt)
        time.sleep(0.01)

#       TODO organize this server script into a class.
threading.Thread(target=updatePlayers).start()
threading.Thread(target=gameThread).start()

while True:
  conn, addr = server.accept()
  threading.Thread(target=clientThread, args=(conn, addr)).start()


conn.close()
server.close()
