from card_ import DUMMY_CARDS
from game_util import *
from net_util import *

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QStatusBar, QMenuBar, QMenu, QAction, QGridLayout, QMessageBox
from PyQt5.QtGui import QImage, QIcon, QPainter, QTextOption
from PyQt5.QtCore import QPoint, QSize, QRect, QRectF, pyqtSignal, Qt
from PIL import Image
from PIL.ImageQt import ImageQt
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time
import pickle
import sys

my_name = 'TestPlayer'

server_ip = '127.0.0.1'
server_port = 34567

_ICON_WIDTH = _ICON_HEIGHT = 20

def inform_alive(client_socket):
    '''
    主动发送hi告知server自己依然alive
    '''
    while True:
        client_socket.sendall(b'@!hi')
        time.sleep(5)


class Gui(QMainWindow):
    connection_toggled = pyqtSignal(bool)
    ready_toggled = pyqtSignal(bool)
    msg_arrived = pyqtSignal(bytes)
    chupai_toggled = pyqtSignal(bool)
    dispose_clicked = pyqtSignal()
    pass_clicked = pyqtSignal()
    game_end = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player = Player()
        self.start_game = False
        self.chupai_activated = False
        self.player.name = my_name
        self.player2_num_card = self.player3_num_card = 0
        self.player2_name = self.player3_name = 'NO_NAME'
        self.dispose_region = QRect(0, 0, 0, 0)
        self.pass_region = QRect(0, 0, 0, 0)
        self.chulepai = [None, None, None]
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.index = -1  # 编号

        self._ui_setup()

        self.connection_toggled.connect(self.connection_toggled_action)
        self.ready_toggled.connect(self.ready_toggled_action)
        self.msg_arrived.connect(self.process_message)
        self.chupai_toggled.connect(self.chupai_toggled_action)
        self.player.card_changed.connect(self.central_label.repaint)
        self.dispose_clicked.connect(self.dispose_clicked_action)
        self.pass_clicked.connect(self.pass_clicked_action)
        self.game_end.connect(self.game_end_action)

        self.connection_toggled.emit(False)
        self.show()

    def _ui_setup(self):
        self.setWindowTitle('三人争上游')
        self.setWindowIcon(QIcon(os.path.join('.', 'image', 'icon.ico')))
        self.resize(800, 600)
        self.status_bar = self.statusBar()
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('&Game')
        self.help_menu = self.menu_bar.addMenu('&Help')
        self.connect_action = self.file_menu.addAction('&Connect')
        self.connect_action.setShortcut('F5')
        self.connect_action.triggered.connect(self.connect_to_server)
        self.ready_action = self.file_menu.addAction('&New game')
        self.ready_action.setShortcut('F2')
        self.ready_action.triggered.connect(self.say_ready)
        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction('E&xit')
        self.exit_action.setShortcut('ctrl+q')
        self.exit_action.triggered.connect(self.close)
        
        self.central_label = self.CentralLabel(self)
        self.setCentralWidget(self.central_label)
        self.central_label.repaint()
        
    class CentralLabel(QLabel):
        def __init__(self, gui):
            super().__init__()
            self.gui = gui
            self.player1_card_image_position = QPoint(0, (self.height() - card_image_height) * 0.9)
            self.player1_card_image_size = QSize(0, 0)

        def paintEvent(self, event):
            painter = QPainter(self)
            if self.gui.start_game:
                # player1 card_image
                if self.gui.player.cards is not None and len(self.gui.player.cards) > 0:
                    card_image = ImageQt(get_cards_image(self.gui.player.cards))
                    label_size = self.size()
                    self.player1_card_image_size = card_image.size()
                    self.player1_card_image_position.setX((label_size.width() - self.player1_card_image_size.width()) * 0.5)
                    self.player1_card_image_position.setY((label_size.height() - self.player1_card_image_size.height()) * 0.97)
                    painter.drawImage(self.player1_card_image_position, card_image)
                # player1 name
                up = self.player1_card_image_position.y() + card_image_height
                painter.drawText(QRect(0, up, self.width(), self.height() - up), Qt.AlignCenter, '{} ({})'.format(self.gui.player.name, len(self.gui.player.cards)))
                # player1 chulepai
                card_image = ImageQt(get_cards_image(self.gui.chulepai[0]))
                image_x = (self.width() - card_image.width()) * 0.5
                image_y = (self.player1_card_image_position.y() - card_image.height()) * 0.85
                painter.drawImage(image_x, image_y, card_image)
                # dispose, pass
                if self.gui.chupai_activated:
                    image_x = (self.width() - _ICON_WIDTH) * 0.47
                    image_y = self.player1_card_image_position.y() * 0.94
                    painter.drawImage(image_x, image_y, QImage(os.path.join('.', 'image', 'dispose.png')))
                    self.gui.dispose_region.setCoords(image_x, image_y, image_x + _ICON_WIDTH, image_y + _ICON_HEIGHT)
                    image_x = (self.width() - _ICON_WIDTH) * 0.53
                    painter.drawImage(image_x, image_y, QImage(os.path.join('.', 'image', 'pass.png')))
                    self.gui.pass_region.setCoords(image_x, image_y, image_x + _ICON_WIDTH, image_y + _ICON_HEIGHT)
                # player2 card_image, name
                card_image = ImageQt(get_cards_back(self.gui.player2_num_card).transpose(Image.ROTATE_90))
                image_x = (self.width() - card_image.width()) * 0.95
                image_y = (self.height() - card_image.height()) * 0.15
                painter.drawImage(image_x, image_y, card_image)
                painter.drawText(QRect(image_x, image_y * 0.5, card_image.width(), image_y * 0.5), Qt.AlignCenter, '{} ({})'.format(self.gui.player2_name, self.gui.player2_num_card))
                # player2 chulepai
                card_image = ImageQt(get_cards_image(self.gui.chulepai[1], wrap=8))
                image_x = image_x * 0.95 - card_image.width()
                image_y = (self.height() - card_image.height()) * 0.15
                painter.drawImage(image_x, image_y, card_image)
                # player3 card_image, name
                card_image = ImageQt(get_cards_back(self.gui.player3_num_card).transpose(Image.ROTATE_90))
                image_x = (self.width() - card_image.width()) * 0.05
                image_y = (self.height() - card_image.height()) * 0.15
                painter.drawImage(image_x, image_y, card_image)
                painter.drawText(QRect(image_x, image_y * 0.5, card_image.width(), image_y * 0.5), Qt.AlignCenter, '{} ({})'.format(self.gui.player3_name, self.gui.player3_num_card))
                # player3 chulepai
                image_x = image_x + card_image.width()
                card_image = ImageQt(get_cards_image(self.gui.chulepai[2], wrap=8))
                image_x += (self.width() - image_x) * 0.05
                image_y = (self.height() - card_image.height()) * 0.15
                painter.drawImage(image_x, image_y, card_image)
    

        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton:
                mouse_x = event.x()
                mouse_y = event.y()
                num_cards = len(self.gui.player.cards)
                if num_cards > 0:
                    if self.player1_card_image_position.x() <= mouse_x <= self.player1_card_image_position.x() + self.player1_card_image_size.width() and self.player1_card_image_position.y() <= mouse_y <= self.player1_card_image_position.y() + self.player1_card_image_size.height():
                        index = (mouse_x - self.player1_card_image_position.x()) // card_left
                        if index >= num_cards:
                            index = num_cards - 1
                        self.gui.player.cards.toggle_select(self.gui.player.cards[index])
                if self.gui.chupai_activated:
                    if self.gui.dispose_region.left() <= mouse_x < self.gui.dispose_region.right() and self.gui.dispose_region.top() <= mouse_y < self.gui.dispose_region.bottom():
                        self.gui.dispose_clicked.emit()
                    elif self.gui.pass_region.left() <= mouse_x < self.gui.pass_region.right() and self.gui.pass_region.top() <= mouse_y < self.gui.pass_region.bottom():
                        self.gui.pass_clicked.emit()


    def connect_to_server(self):
        try:
            self.client_socket.connect((server_ip, server_port))
        except Exception:
            self.status_bar.showMessage('连接失败')
            return
        connection_msg = self.client_socket.recv(2048).decode().rstrip()
        if connection_msg.startswith('connection_OK'):
            self.status_bar.showMessage('连接成功，按F2开始游戏')
            self.connection_toggled.emit(True)
            _, index = connection_msg.split(' ')
            self.index = int(index)
            Thread(target=inform_alive, args=(self.client_socket,), daemon=True).start()
            self.client_socket.sendall(('@!set_name ' + my_name).encode())
        else:
            self.status_bar.showMessage(connection_msg)

    def connection_toggled_action(self, connection_established):
        self.connect_action.setEnabled(not connection_established)
        self.ready_action.setEnabled(connection_established)
        if connection_established:
            Thread(target=self.get_message, daemon=True).start()

    def say_ready(self):
        self.client_socket.sendall(b'@!ready')
        self.chulepai = [None, None, None]
        self.chupai_toggled.emit(False)
        self.ready_toggled.emit(True)

    def ready_toggled_action(self, ready):
        self.ready_action.setEnabled(not ready) 

    def chupai_toggled_action(self, chupai_activated):
        self.chupai_activated = chupai_activated
        if chupai_activated:
            self.chulepai[0] = []
            self.central_label.repaint()
        self.central_label.repaint()

    def get_message(self):
        for msg in get_msg(self.client_socket):
            self.msg_arrived.emit(msg)

    def process_message(self, msg):
        if msg.startswith(b'!'):
            if msg.startswith(b'!names'):
                names = msg[len(b'!names '):].decode().split('\t')
                i = 2 if self.index == 0 else self.index - 1
                self.player2_name = names[i]
                i = 2 if i == 0 else i - 1
                self.player3_name = names[i]
            elif msg.startswith(b'!serve'):
                self.start_game = True
                cards = cards_decode(msg[len(b'!serve '):])
                self.player2_num_card = len(cards)
                self.player3_num_card = len(cards)
                self.player.get_served(cards)
                self.passed_players = 0
                self.current_card = DUMMY_CARDS
            elif msg.startswith(b'!info'):
                self.status_bar.showMessage(msg[len(b'!info '):].decode())
            elif msg.startswith(b'!chupai'):
                who = int(msg[len(b'!chupai '):].decode())
                if who == self.index:
                    if self.passed_players >= NUM_PLAYER - 1:
                        self.passed_players = 0
                        self.current_card = DUMMY_CARDS
                    self.chupai_toggled.emit(True)
                    self.status_bar.showMessage('轮到你出牌')
                else:
                    self.status_bar.showMessage('轮到{}出牌'.format(self._get_name(who)))
            elif msg.startswith(b'!chulepai'):
                who = int(msg[len(b'!chulepai ') : len(b'!chulepai ') + 1].decode())
                disposed_card = cards_decode(msg[len(b'!chulepai ') + 2 :])
                self.current_card = disposed_cards(disposed_card, CardType.parse(''.join([card.to_character() for card in disposed_card])))
                self.passed_players = 0
                self._set_chulepai(who)
            elif msg.startswith(b'!passed'):
                who = int(msg[len(b'!passed '):].decode())
                self.passed_players += 1
                self._set_passed(who)
                

    def dispose_clicked_action(self):
        cards = [card for card in self.player.cards if card.selected]
        card_type = chupai_ok(cards, self.current_card.card_type)
        if card_type is not None:
            self.current_card = disposed_cards(cards, card_type)
            self.player.chupai(cards)
            self.client_socket.sendall(b'@!chupai ' + cards_encode(cards))
            self._set_chulepai(self.index)
            self.passed_players = 0
            self.chupai_toggled.emit(False)
        else:
            self.status_bar.showMessage('不能出此牌')

    def pass_clicked_action(self):
        if self.current_card is not DUMMY_CARDS:
            self.client_socket.sendall(b'@!pass')
            self.passed_players += 1
            self._set_passed(self.index)
            self.chupai_toggled.emit(False)
            for card in self.player.cards:
                card.selected = False
            self.central_label.repaint()
        else:
            self.status_bar.showMessage('请出牌')
            
    def _get_name(self, index):
        if index == self.index:
            return self.player.name
        index = 2 if index == 0 else index - 1
        if index == self.index:
            return self.player2_name
        index = 2 if index == 0 else index - 1
        if index == self.index:
            return self.player3_name
        return ''

    def _set_chulepai(self, index):
        if index == self.index:
            self.chulepai[0] = self.current_card.cards
            if len(self.player.cards) == 0:
                QMessageBox.information(self, 'You Win', 'You win!')
                self.game_end.emit()
                self.client_socket.sendall(b'@!gameend ' + str(self.index).encode())
        else:
            index = 2 if index == 0 else index - 1
            if index == self.index:
                self.chulepai[1] = self.current_card.cards
                self.player2_num_card -= len(self.current_card.cards)
                if self.player2_num_card == 0:
                    QMessageBox.information(self, 'Game Over', self.player2_name + ' wins!')
                    self.game_end.emit()
            else:
                self.chulepai[2] = self.current_card.cards
                self.player3_num_card -= len(self.current_card.cards)
                if self.player3_num_card == 0:
                    QMessageBox.information(self, 'Game Over', self.player3_name + ' wins!')
                    self.game_end.emit()
        self.central_label.repaint()

    def _set_passed(self, index):
        if index == self.index:
            self.chulepai[0] = 'pass'
        else:
            index = 2 if index == 0 else index - 1
            if index == self.index:
                self.chulepai[1] = 'pass'
            else:
                self.chulepai[2] = 'pass'
        self.central_label.repaint()

    def game_end_action(self):
        self.start_game = False
        self.ready_toggled.emit(False)
        self.status_bar.showMessage('按F2进入下一轮游戏...')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Gui()
    '''
    list_players = [Player(), Player(), Player()]
    import server_logic
    server_logic.serve(list_players)
    gui.player.get_served(list_players[0].cards.cards)
    gui.chulepai[0] = gui.player.cards.cards
    gui.chulepai[1] = gui.player.cards.cards
    gui.chulepai[2] = gui.player.cards.cards
    '''
    sys.exit(app.exec_())
