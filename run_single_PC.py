from game_util_single_PC import *
from game_logic_single_PC import *

player_names = ['Player1', 'Player2', 'Player3']
for player, name in zip(list_players, player_names):
    player.name = name

start_game()

input()
