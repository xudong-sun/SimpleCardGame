# Chinese Card Game "������"
## Overview
- 3-person ������ game with one set of (54) cards
- played over the network
- written in Python3.4 + PyQt5.5
![game snapshot](image/game-snapshot.png)

## Instructions
1. Run `python card_server.py` to start the server.
2. Run `python card_client.py` to start the client. Using the menu (or shortcut keys), connect to the server and hit "start game". Remember to change ip and port number beforehand. (I plan to make it a config file later)
3. Once 3 people have hit "start game", the game will automatically start.
4. When each round of game is over, hit "start game" again.

## Game Rules
| Allowed Card Set | Example |
|:----------------:|:-------:|
| ����             | 3, 4 |
| ����             | 33, 44 |
| ����             | 333, 444 |
| ����һ           | 3334, JJJ3 |
| ������           | 33344, JJJ33 |
| ˳��(5������)    | A2345, TJQKA, 3456789 |
| ���ö�(3������)  | AA2233, QQKKAA, 33445566 |
| ���             | AAA222, KKKAAA, 333444555 |
| �ɻ�             | AAA2223344, KKKAAA5566, 333444555778899 |
| �Ĵ���           | 333357, 222234 |
| ը��             | 3333, 4444 |

Written by Xudong
2016-05-02