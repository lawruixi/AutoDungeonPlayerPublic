from classes_functions_game_handlers import Turn,Map,Player,Character,dumb_ai,constants,generate_movement
import sys
from mcts import MonteCarlo,Node

debug_disable_dumbai = True
debug_disable_smartai = True
debug_functions = [constants.PLAYER_MELEE_ATTACK((2,3)),constants.PLAYER_MELEE_ATTACK((2,3))]
toggleable_AUTO_END = True
map_size,wall_chance,enemy_count = 3,5,5


while True:
        turn = Turn(map_size,wall_chance,enemy_count)
        movement_sequences = generate_movement((0,0),turn.mapp,(map_size-1,map_size-1),[],[],True)
        if movement_sequences[0] and len(turn.characters)>=2:
            break
    
"""
turn.set_preset([
    ["-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "x"],
    ["#", "o", "-", "-", "x"],
    ["-",  "-", "x", "-", "a"]
])
"""
turn.set_preset([
    ["-", "-", "-", "-", "-"],
    ["-", "x", "-", "-", "-"],
    ["-", "-", "-", "-", "-"],
    ["#", "o", "x", "-", "-"],
    ["-",  "-", "x", "-", "a"]
])

num = 0

while turn.player_dead!=1 and len(turn.characters)>toggleable_AUTO_END:
    turn.determine_action_sequence()
    if turn.check_game_over():
        break
    while True:
        i = turn.current_turn()
        #print(i)
        turn.reset_stance(i)
        if turn.check_game_over():
            break
        while True:
            if turn.check_game_over():
                break
            if turn.check_is_dead(i):
                print("Was dead\n")
                break
            elif turn.check_end_turn():
                print("Turn Ended\n")
                break
            elif (not isinstance(i,Player)) and isinstance(i,Character):
                #print("\n --- AI'S TURN ---")
                if debug_disable_dumbai == False:
                    for a in range(constants.AI_MOVEMENT_POINTS):
                        if not dumb_ai(i,turn.mapp):
                            i.movement_points = 0
                            break
                else:
                    i.movement_points = 0
            elif isinstance(i,Player):
                print("\n --- PLAYER'S TURN ---")
                #call function to get movements
                if debug_disable_smartai == False:
                    initial_node = Node(turn)
                    mcts = MonteCarlo(initial_node)
                    mcts.take_turn()
                    #actions = mcts.get_best_actions()
                    actions_functions = mcts.get_best_actions_functions()
                    mcts.print_node_tree()
                    #action_functions contains an array [action1, action2] where action1 and action2 are the lambda functions
                    #i.e. MOVE_PLAYER(n), PLAYER_ATTACK(n), PLAYER_BLOCK(n);
                    #print(actions_functions)
                    for action in actions_functions:
                        if action !=None:
                            action(i,turn.mapp)
                    num+=1
                elif len(debug_functions)>0:
                        print(i.possible_melee_attack_coordinates_this_turn(turn.mapp))
                        (debug_functions.pop())(i,turn.mapp)
                        #print(i.position)
                else:
                    turn.lose = 1

        if num>1000:
            turn.lose = 1
            break

        print("\nTurn "+str(num+1)+" Character: "+str(i))
        turn.mapp.print_array()

print("\n\n\nFinal Map State\n")
turn.mapp.print_array()