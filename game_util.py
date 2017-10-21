from card_type import *
from card_ import *

from PyQt5.QtCore import pyqtSignal, QObject
import random

NUM_PLAYER = 3
NUM_SUITE = 1

class Player(QObject):
    card_changed = pyqtSignal()

    def __init__(self, name=''):
        super().__init__()
        self.cards = Cards(self);
        self.name = name
        self.ready = False

    def get_served(self, cards):
        '''
        cards: list of Card
        return: None
        '''
        cards.sort(key=lambda x: card_characters.index(x.card_point))
        self.cards.set_cards(cards)

    def cards_left(self):
        return len(self.cards)

    def chupai(self, cards):
        '''
        cards: list of Cards
        return: int, cards_left
        '''
        self.cards.dispose(cards)
        return self.cards_left()

    def __str__(self):
        return self.name


class Cards(QObject):
    card_changed = pyqtSignal()

    def __init__(self, owner):
        '''
        owner: Player
        '''
        super().__init__()
        self.cards = None
        self.owner = owner
        self.card_changed.connect(self.owner.card_changed)

    def set_cards(self, cards):
        '''
        cards: list of Card
        '''
        self.cards = cards
        self.card_changed.emit()

    def dispose(self, cards):
        '''
        cards: list of Card
        '''
        try:
            for card in cards:
                self.cards.remove(card)
        except ValueError:
            raise GameLogicError('{} does not have card {}'.format(self.owner, card))
        self.card_changed.emit()

    def toggle_select(self, card):
        if card not in self.cards:
            raise GameLogicError('{} does not have card {}'.format(self.owner, card))
        card.toggle_select()
        self.card_changed.emit()

    def __len__(self):
        return 0 if self.cards is None else len(self.cards)
    
    def __iter__(self):
        return self.cards.__iter__()

    def __getitem__(self, index):
        return self.cards[index]

    def __setitem__(self, index, value):
        self.cards[index] = value
    
    def __str__(self):
        return to_card_string(self.cards)


def chupai_ok(cards, previous):
    '''
    检查出牌是否合法
    cards: Cards, or list of Card
    previous: CardType, 上一轮出的牌
    return: card_type / None
    '''
    card_string = ''.join([card.to_character() for card in cards if card.selected])
    card_type = CardType.parse(card_string)

    if card_type is None:
        return None
    if card_type > previous:
        return card_type


def serve(list_players):
    if len(list_players) != NUM_PLAYER:
        raise GameLogicError('Number of players is not ' + NUM_PLAYER)
    all_cards = []
    for i in range(NUM_SUITE):
        for suit in 'CDHS':
            for card_point in card_characters[:13]:
                all_cards.append(Card(suit + card_point))
        all_cards.append(Card('JS'))
        all_cards.append(Card('JB'))
    random.shuffle(all_cards)
    num_card_each = len(all_cards) // NUM_PLAYER
    for index, player in enumerate(list_players):
        player.get_served(all_cards[num_card_each * index : num_card_each * (index+1)])


def take_turns():
    for index in range(random.randint(0, NUM_PLAYER - 1), NUM_PLAYER):
        yield index
    while True:
        for index in range(NUM_PLAYER):
            yield index


def cards_encode(cards):
    '''
    cards: Cards, or list of Card
    return: bytes
    '''
    ss = ''
    for card in cards:
        ss += str(card)
    return ss.encode()


def cards_decode(cards_bytes):
    '''
    return: list of Cards
    '''
    cards_str = cards_bytes.decode()
    cards = []
    if len(cards_str) % 2 != 0:
        raise GameLogicError('Failed to decode cards_bytes')
    for suit, card_point in zip(cards_str[::2], cards_str[1::2]):
        cards.append(Card(suit + card_point))
    return cards


class GameEnd(Exception):
    def __init__(self, winner):
        self.winner = winner


class GameLogicError(Exception): pass
