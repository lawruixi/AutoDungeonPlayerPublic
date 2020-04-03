'''
Tests from core_functions.py
'''
from classes_functions_game_handlers import Turn,Map,Player,Character,dumb_ai,Constants,generate_movement
import sys
from mcts import MonteCarlo,Node
import matplotlib.pyplot as plt
from graph import *

PLAYER_MOVE = lambda z: (lambda x,y: x.move(z,y))
PLAYER_MELEE_ATTACK = lambda z: (lambda x,y: x.attack_melee(z,y))
PLAYER_RANGED_ATTACK = lambda z: (lambda x,y: x.attack_ranged(z,y))
PLAYER_BLOCK = lambda z: (lambda x,y: x.block())


toggleable_AUTO_END = 0#1 to auto end if all enemies are dead, 0 to disable


#if not __name__ == "__main__":
    #sys.exit(0)


def read_and_run_test_runs(filename):
    """
    Will run cases that are written in following format in input file:

    Testcase,AI_move_pts,AI_"hp,AI_attk,AI_move,player_move_pts,player_hp,player_attk,player_move,map_size,wall_chance,enemy_count,N,output_file
    where N is the number of times to run with that setup
    """
    input_file = open(filename,"r")
    for line in input_file:
        #print(line)
        case = line.strip().split(",")
        #print(case)
        if (case[0] == "Testcase"):
            data = case[1:]
            runs = int(data[-2])
            output_file = open(data[-1],"w")
            output = []
            AI_move_pts,AI_hp,AI_attk,AI_move,player_move_pts,player_hp,player_melee_attk,player_ranged_attk,player_min_ranged_range,player_ranged_range,player_move,map_size = (int(i) for i in data[0:-4])
            wall_chance = float(data[-4])
            enemy_count = int(data[-3])
            for i in range(runs):
                output.append(play_game(data[0:-2]))
            #print(output)
            for i in output:
                output_file.write(i)
                output_file.write("\n")

            json_dict ={
                "Total stats": ".",
                "Enemy Count": enemy_count,
                "Wall Chance": wall_chance,
                "Map Size": map_size,
                "AI Health": AI_hp,
                "AI Movement Points": AI_move_pts,
                "AI Movement Speed": AI_move,
                "AI Attack": AI_attk,
                "Player Health": player_hp,
                "Player Movement Points": player_move_pts,
                "Player Movement Speed": player_move,
                "Player Melee Attack": player_melee_attk,
                "Player Ranged Attack": player_ranged_attk,
                "Player Ranged Range" : player_ranged_range,
                "Player Ranged Min Range": player_min_ranged_range
            }
            output_file.write(json.dumps(json_dict))
            output_file.close()
    input_file.close()


def play_game(data):
    AI_move_pts,AI_hp,AI_attk,AI_move,player_move_pts,player_hp,player_melee_attk,player_ranged_attk,player_min_ranged_range,player_ranged_range,player_move,map_size = (int(i) for i in data[0:-2])
    wall_chance = float(data[-2])
    enemy_count = int(data[-1])
    constantss = Constants()
    constantss.custom_game(AI_move_pts,AI_hp,AI_attk,AI_move,player_move_pts,player_hp,player_melee_attk,player_move,player_ranged_attk,player_ranged_range,player_min_ranged_range)
    while True:
        turn = Turn(map_size,wall_chance,enemy_count,constantss)
        movement_sequences = generate_movement((0,0),turn.mapp,(map_size-1,map_size-1),[],[],True)
        if movement_sequences[0] and len(turn.characters)>=2:
            break

    num = 0
    while turn.player_dead!=1 and len(turn.characters)>toggleable_AUTO_END:
        turn.determine_action_sequence()
        if turn.check_game_over():
            break
        while True:
            i = turn.current_turn()
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
                    print("\n --- AI'S TURN ---")
                    for a in range(constantss.AI_MOVEMENT_POINTS):
                        if not dumb_ai(i,turn.mapp):
                            i.movement_points = 0
                            break
                elif isinstance(i,Player):
                    #call function to get movements
                    print("\n --- PLAYER'S TURN ---")
                    mcts = MonteCarlo(constantss, turn)
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
            if num>1000:
                turn.lose = 1
                break

            print("\nTurn "+str(num+1)+" Character: "+str(i))
            turn.mapp.print_array()

    print("\n\n\nFinal Map State\n")
    turn.mapp.print_array()
    win_state = False
    kill_count = max(turn.dead_counter-turn.player_dead,0) #hotfix for -1 killcount
    if turn.check_win():
        win_state = True
        print("WIN")
    if turn.check_lose():
        win_state = False
        print("LOSE")
    json_dict = {



            "Win_state": win_state,
            "Kills": kill_count,
            "Turns": num,
            "Health": turn.player.health,

        }

    return json.dumps(json_dict)

# print(play_game((1,20,10,20,2,50,20,10,5,5,10)))
#print(play_game((1,20,10,50,2,100,50,10,1,3,10,5,5,5)))
read_and_run_test_runs("input2.csv")
#read_and_intepret("initial_testing.txt")

#read_and_graph(["initialtesting1.txt","initialtesting2.txt","initialtesting3.txt"],"Wall Chance","Win Percentage")
#read_and_graph(["initialtesting4.txt","initialtesting5.txt"],"Enemy Count","Win Percentage")
#read_and_graph(["initialsmalltesting62.txt","initialsmalltesting72.txt","initialsmalltesting82.txt","initialsmalltesting92.txt","initialsmalltesting102.txt","initialsmalltesting112.txt"],"Player Health","Win Percentage")
#read_and_graph(["initialtesting2.txt","initialtesting1.txt"],"AI Health","Win Percentage")
"""print coordinates of possible melee attacks"""
