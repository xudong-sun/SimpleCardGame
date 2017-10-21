from card_type import *

import random

NUM_PLAYER = 3
NUM_SUITE = 1

class Player:
    def __init__(self):
        self.cards = "";

    def get_served(self, cards):
        '''
        cards: str
        return: None
        '''
        self.cards = sort_card_string(cards)

    def cards_left(self):
        return len(self.cards)

    def chupai(self, card_string):
        '''
        card_string: str, new string
        return: int, cards_left
        '''
        for ch in card_string.upper():
            if ch in self.cards:
                self.cards = self.cards.replace(ch, '', 1)
            else:
                raise GameLogicError()
        return self.cards_left()


def chupai_ok(card_string, previous, all_cards):
    '''
    检查出牌是否合法
    card_string: str, 要出的牌
    previous: CardType, 上一轮出的牌
    all_cards: str, 你拥有的牌
    return: card_type / None
    '''
    card_string = card_string.upper()
    for ch in card_string:
        if ch not in all_cards:
            return None
        all_cards = all_cards.replace(ch, '', 1)
    card_type = CardType.parse(card_string)

    if card_type is None:
        return None
    if card_type > previous:
        return card_type


def serve(list_players):
    all_cards = ('A23456789TJQK' * 4 + 'SB') * NUM_SUITE
    temp = list(all_cards)
    random.shuffle(temp)
    all_cards = ''.join(temp)
    num_card_each = len(all_cards) // NUM_PLAYER
    for index, player in enumerate(list_players):
        player.get_served(all_cards[num_card_each * index : num_card_each * (index+1)])


def take_turns(list_players):
    '''
    generator. randomize the first turn. yields a player in turn
    '''
    for player in list_players[random.randint(0, NUM_PLAYER-1):]:
        yield player
    while True:
        for player in list_players:
            yield player


class GameEnd(Exception): 
    def __init__(self, winner):
        self.winner = winner
