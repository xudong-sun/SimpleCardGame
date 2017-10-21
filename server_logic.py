from card_ import *
from game_util import *

import pickle
import random
import time
from collections import deque
from threading import Lock


WARN_NUM_CARD = 5
list_players = [Player() for index in range(NUM_PLAYER)]


def start_game(connection_sockets):
    '''
    return: int, index of winner
    '''
    print('start game')
    send_message_to_all(('@!names {}\t{}\t{}'.format(list_players[0].name, list_players[1].name, list_players[2].name)).encode(), connection_sockets)
    serve(list_players)
    for player, connection_socket in zip(list_players, connection_sockets):
        connection_socket.sendall(b'@!serve ' + cards_encode(player.cards))
    
    # 所有的logic都在client中，server唯一的作用就是传播信息
    try:
        for index in take_turns():
            send_message_to_all(b'!chupai ' + str(index).encode(), connection_sockets)
            chupai_info = server_logic_pipeline.consume()
            if chupai_info.startswith(b'!chupai'):
                disposed_card = cards_decode(chupai_info[len(b'!chupai '):])
                send_message_to_others(index, b'!chulepai ' + str(index).encode() + b' ' + cards_encode(disposed_card), connection_sockets)
            elif chupai_info.startswith(b'!pass'):
                send_message_to_others(index, b'!passed ' + str(index).encode(), connection_sockets)
            elif chupai_info.startswith(b'!gameend'):
                index = int(chupai_info[len(b'!gameend '):].decode())
                raise GameEnd(list_players[index])
            else:
                raise GameLogicError('Message not understood by server')
    except GameEnd as game:
        return game.winner


class LogicPipeline(deque):
    '''
    由client发送的消息一部分会被导入这个pipeline，交由start_game部分处理
    '''
    def __init__(self):
        self.lock = Lock()

    def consume(self):
        while True:
            self.lock.acquire()
            if len(self) > 0:
                string = self.popleft()
                self.lock.release()
                return string
            else:
                self.lock.release()
                time.sleep(0.5)

    def append(self, string):
        self.lock.acquire()
        super().append(string)
        self.lock.release()
        

server_logic_pipeline = LogicPipeline()


def send_message_to_others(index, message, connection_sockets):
    '''
    将message发送给除自己以外的所有人
    index: int, 你是谁，编号
    message: str, bytestring
    connection_sockets: list
    '''
    for connection_socket in connection_sockets:
        if connection_sockets[index] is not connection_socket:
            connection_socket.sendall(b'@' + message)

def send_message_to_all(message, connection_sockets):
    '''
    将message发送给所有人
    message: str, bytestring
    connection_sockets: list
    '''
    for connection_socket in connection_sockets:
        connection_socket.sendall(b'@' + message)

