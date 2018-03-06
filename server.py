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

server.listen(2000)

game = Game()

clients = []

def clientThread(conn, addr):
    print("Connection started")
    print(addr)
    message = conn.recv(2048)
    print(message.decode())
    game.add_player(strip_special(message.decode()), COLORS.pop())
    conn.send(game.get_map().encode())
    time.sleep(2)
    clients.append(conn)

    while True:
        try:
            message = conn.recv(2048)
            if message:
                game.input(*message.decode().split(":"))
        except:
          continue

def strip_special(string):
    return string.replace(":", "").replace(";", "").replace(",", "")
def updatePlayers():
    state = None
    while True:
        new_state = game.get_state()
        if new_state != state:
            state = new_state
            for client in clients:
                try:
                    client.send(new_state.encode())
                except:
                    client.close()
                    if client in clients:
                        clients.remove(client)
        time.sleep(0.05)

def gameThread():
    t = time.time()
    while True:
        new_t = time.time()
        dt = new_t - t
        t = new_t
        game.update(dt)
        time.sleep(0.01)

threading.Thread(target=updatePlayers).start()

threading.Thread(target=gameThread).start()
while True:
  conn, addr = server.accept()
  threading.Thread(target=clientThread, args=(conn, addr)).start()


conn.close()
server.close()
