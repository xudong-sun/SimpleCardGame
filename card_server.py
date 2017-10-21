from socket import *
from game_util import NUM_PLAYER
from server_logic import *
from net_util import *

from threading import Thread
import time

server_port = 34567

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen(1)

TIMEOUT = 15

connected_player = 0
connection_sockets = [None] * NUM_PLAYER

def everyone_ready():
    for player in list_players:
        if player.ready is False:
            return False
    return True

def close_connection(index):
    if connection_sockets[index] is not None:
        connection_sockets[index].close()
        print('connection ' + str(index) + ' closed')
        connection_sockets[index] = None


def service(index):
    connection_socket = connection_sockets[index]
    player = list_players[index]
    for msg in get_msg(connection_socket):
        # 如果#后的消息由!开头，表示特殊指令；否则根据发送列表，将消息传给对应的socket
        if msg.startswith(b'!'):
            if msg.startswith(b'!hi'):
                pass
            elif msg.startswith(b'!set_name'):
                player.name = msg[len(b'!set_name '):].decode()
            elif msg.startswith(b'!ready'):
                player.ready = True
                connection_socket.sendall('@!info 正在等待其他玩家...'.encode())
                if everyone_ready():
                    Thread(target=start_game, args=(connection_sockets,), daemon=True).start()
                    for p in list_players:
                        p.ready = False
            elif msg.startswith(b'!close'):
                close_connection(index)
            else:
                server_logic_pipeline.append(msg)
    close_connection(index)


print('server starts operating')
while True:
    connection_socket, client_ip = server_socket.accept()
    for index, cs in enumerate(connection_sockets):
        if cs is None:
            print('new connection ' + str(index))
            connection_sockets[index] = connection_socket
            connection_socket.settimeout(TIMEOUT)
            list_players[index].ready = False
            Thread(target=service, args=(index,), daemon=True).start()
            connection_socket.sendall(('connection_OK ' + str(index)).encode())
            break
    else:
        connection_socket.sendall(b'Number of connected players exceeds maximum')
        connection_socket.close()
