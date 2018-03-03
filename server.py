import socket
import sys
import threading
from game import Game
import time
from constants import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP_address = '192.168.33.160'
PORT = 52801

server.bind((IP_address,PORT))

server.listen(20000)

game = Game()

clients = []

def clientThread(conn, addr):
    print("Connection started")
    print(addr)

    message = conn.recv(2048)
    game.add_player(message.decode(), COLORS.pop())
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

def updatePlayers():
    t = time.time()
    while True:
        new_t = time.time()
        dt = new_t - t
        t = new_t
        game.update(dt)
        for client in clients:
            try:
                client.send(game.get_state().encode())
            except:
                client.close()
                if client in clients:
                    clients.remove(client)
        time.sleep(0.05)

threading.Thread(target=updatePlayers).start()

while True:
  conn, addr = server.accept()
  threading.Thread(target=clientThread, args=(conn, addr)).start()

conn.close()
server.close()
