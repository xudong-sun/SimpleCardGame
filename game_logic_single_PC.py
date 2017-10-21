from card_type import *
from game_util_single_PC import *
import os

WARN_NUM_CARD = 5
list_players = [Player() for index in range(NUM_PLAYER)]


def start_game():
    '''
    single-PC version
    return: player, winner
    '''
    serve(list_players)
    
    passed_players = 0
    current_card = DUMMY
    
    for player in take_turns(list_players):
        os.system('cls')
        print('{}, your turn now!\nPrevious: {}\nYour cards left: {}\n'.format(player.name, current_card, player.cards))
        try:
            while True:
                card_string = input('Qing Chu Pai: ')
                if card_string.lower() == 'pass' and current_card is not DUMMY:
                    passed_players += 1
                    if passed_players == NUM_PLAYER - 1:
                        passed_players = 0
                        current_card = DUMMY
                    break
                current_card = chupai_ok(card_string, current_card, player.cards)
                if current_card is not None:
                    cards_left = player.chupai(card_string)
                    passed_players = 0
                    if cards_left == 0:
                        print(player.name+" wins!")
                        raise GameEnd(player)
                    elif cards_left <= WARN_NUM_CARD:
                        print('{} has only {} card{} left!'.format(player.name, cards_left, 's' if cards_left > 1 else ''))
                    break
                print('invalid card_string')
        except GameEnd as game:
            return game.winner
