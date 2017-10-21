from card_type import card_characters, sort_card_string, DUMMY_TYPE

from PyQt5.QtCore import pyqtSignal, QObject
from PIL import Image
from collections import namedtuple
import os


card_image_width, card_image_height = 75, 115
card_left = 12
_card_up = 32
_card_selected = 10

_image_row = {'C': (359, 475), 'D': (2, 118), 'H': (121, 237), 'S': (240, 355), 'J': (478, 593)}
_image_column = ((159, 235), (238, 313), (317, 392), (396, 471), (475, 549), (553, 628), (632, 707), (711, 785), (789, 864), (868, 943), (947, 1021), (2, 77), (81, 156), (81, 156), (2, 77))
_image_all = Image.open(os.path.join('.', 'image', 'all.jpg'))

disposed_cards = namedtuple('disposed_cards', ['cards', 'card_type'])
DUMMY_CARDS = disposed_cards([], DUMMY_TYPE)


class Card(object):
    def __init__(self, card_string):
        '''
        card_string: str, 长度为2. 第一个字符为CDHSJ中的一个，代表花色（J代表大小怪），第二个字符为A23456789TJQKSB中的一个
        '''
        super().__init__()
        card_string = card_string.upper()
        if card_string[0] not in 'CDHSJ' or card_string[1] not in card_characters:
            raise CardError('invalid card string ' + card_string)
        self.suit = card_string[0]
        self.card_point = card_string[1]
        self.selected = False
        self.image = self._get_image()

    def to_character(self):
        '''
        return: char
        '''
        return self.card_point

    def toggle_select(self):
        self.selected = not self.selected

    def _get_image(self):
        left, right = _image_column[card_characters.index(self.card_point)]
        up, down = _image_row[self.suit]
        return _image_all.crop((left, up, right, down)).resize((card_image_width, card_image_height))

    def __str__(self):
        return self.suit + self.card_point


def to_card_string(cards):
    '''
    cards: list of Card
    return: str, sorted
    '''
    card_string = ''
    for card in cards:
        card_string += card.to_character()
    return sort_card_string(card_string)


class CardError(Exception): pass


def get_cards_image(cards, wrap=100):
    '''
    cards: Cards, or a list, or 'pass'
    wrap: int, 一排最多放几张牌
    return: Image
    '''
    def position(index):
        '''
        index: int
        return: (x, y)
        '''
        column, row = index % wrap, index // wrap
        return card_left * column, (0 if cards[index].selected else _card_selected) + _card_up * row

    if cards == 'pass':
        pass_image = Image.open(os.path.join('.', 'image', 'passed.png')) 
        image = Image.new('RGBA', (pass_image.width, card_image_height), (255, 255, 255, 0))
        left = (image.width - pass_image.width) // 2
        up = (image.height - pass_image.height) // 2
        image.paste(pass_image, (left, up))
        return image
    if cards is None or len(cards) == 0:
        return Image.new('RGBA', (1, card_image_height), (255, 255, 255, 0))
    num_cards = len(cards)
    width, _ = position(min(num_cards, wrap) - 1)
    width += card_image_width
    _, height = position(num_cards - 1)
    height += card_image_height + (_card_selected if cards[num_cards - 1].selected else 0)
    
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    for index, card in enumerate(cards):
        image.paste(card.image, position(index))
    
    return image


def get_cards_back(num_cards, pattern=1):
    '''
    pattern: int, 背面图案的类型
    return: Image, 牌的背面图案，num_cards张牌
    '''
    if num_cards == 0:
        return Image.new('RGBA', (1, card_image_height), (255, 255, 255, 0))
    back = Image.open(os.path.join('.', 'image', 'back' + str(pattern) + '.jpg'))
    width = card_image_width + card_left * (num_cards - 1)
    height = card_image_height
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    for index in range(num_cards):
        image.paste(back, ((num_cards - 1 - index) * card_left, 0))
    return image

