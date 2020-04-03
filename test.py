from classes_functions_game_objects import *
from classes_functions_game_handlers import *

import mcts

PLAYER_MOVE = lambda z: (lambda x,y: x.move(z,y))
PLAYER_MELEE_ATTACK = lambda z: (lambda x,y: x.attack_melee(z,y))
PLAYER_RANGED_ATTACK = lambda z: (lambda x,y: x.attack_ranged(z,y))
PLAYER_BLOCK = lambda z: (lambda x,y: x.block())

turn = Turn(10, 10, 10)
turn.set_preset([
    ["x", "x", "-", "-"],
    ["-", "o", "-", "-"],
    ["-", "-", "-", "-"],
    ["-", "-", "-", "a"],
    ])

print(turn.characters[1].__str__())
print(turn.player.__str__())
hypo = turn.hypothetical_state([PLAYER_MOVE(0),PLAYER_MOVE(3)])
hypo.mapp.print_array()
