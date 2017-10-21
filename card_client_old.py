from card_type import DUMMY
from game_util import *
from net_util import *

from socket import *
from threading import Thread
import time
import pickle

my_name = 'TestPlayer'

server_ip = '127.0.0.1'
server_port = 34567

def inform_alive(client_socket):
    '''
    主动发送hi告知server自己依然alive
    '''
    while True:
        client_socket.sendall(b'@!hi')
        time.sleep(5)


client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_ip, server_port))

connection_msg = client_socket.recv(2048).decode().rstrip()
if connection_msg.startswith('connection_OK'):
    _, index = connection_msg.split(' ')
    index = str(index)  # 编号
    player = Player()
    Thread(target=inform_alive, args=(client_socket,), daemon=True).start()
    client_socket.sendall(('@!set_name ' + my_name).encode())
    client_socket.sendall(b'@!ready')
    print('欢迎{}'.format(my_name), end='\n\n')

    for msg in get_msg(client_socket):
        if msg.startswith(b'!'):
            if msg.startswith(b'!serve'):
                player.cards = pickle.loads(msg[len(b'!serve '):])
                print('游戏开始\n你发到的牌：' + player.cards, end='\n\n')
                current_card = DUMMY
            elif msg.startswith(b'!info'):
                print(msg[len(b'!info '):].decode(), end='\n\n')
            elif msg.startswith(b'!set_current_card'):
                current_card = pickle.loads(msg[len(b'!set_current_card '):])
            elif msg.startswith(b'!chupai'):
                print('你的牌：' + player.cards)
                while True:
                    card_string = input('轮到你出牌：')

                    if card_string.lower() == 'pass':
                        if current_card is DUMMY:
                            continue
                        else:
                            client_socket.sendall(b'@!pass')
                            break
                    else:
                        current_card = chupai_ok(card_string, current_card, player.cards)
                        if current_card is None:
                            continue
                        else:
                            player.chupai(card_string)
                            client_socket.sendall(b'@!chupai ' + pickle.dumps(current_card))
                            break
            elif msg.startswith(b'!gameend'):
                input('按回车进入下一轮游戏...')
                client_socket.sendall(b'@!ready')
