'''
TODO: Add documentation
'''
from classes_functions_game_handlers import *
from classes_functions_game_objects import *
import math
import sys
import random
import copy

VERBOSE = True
# MOVEMENT_POINTS = constants.PLAYER_MOVEMENT_POINTS
INFINITY = sys.maxsize
MAX_DEPTH = 6; #Maximum embedded statesm before calling a draw

#Maximum time allowed for the computer to Tree Search (in s)
THINKING_TIME = 5

PLAYER_MOVE = lambda z: (lambda x,y: x.move(z,y))
PLAYER_MELEE_ATTACK = lambda z: (lambda x,y: x.attack_melee(z,y))
PLAYER_RANGED_ATTACK = lambda z: (lambda x,y: x.attack_ranged(z,y))
PLAYER_BLOCK = lambda z: (lambda x,y: x.block())


actions_dict = {
    "MOVE_UP" : 1,
    "MOVE_DOWN" : 3,
    "MOVE_LEFT" : 0,
    "MOVE_RIGHT" : 2,

    "MELEE_ATTACK": 10,
    # "RANGED_ATTACK": 11,

    "BLOCK" : -1
}

def print_debug(text="", end='\n'):
    if VERBOSE:
        print(text, end=end)

def is_move(i):
    return i == actions_dict.get("MOVE_UP") or i == actions_dict.get("MOVE_LEFT") or i == actions_dict.get("MOVE_RIGHT") or i == actions_dict.get("MOVE_DOWN")
def is_melee_attack(i):
    if(not isinstance(i, tuple)): return False
    if(len(i) < 3): return False

    return i[0] == actions_dict["MELEE_ATTACK"]
def is_ranged_attack(i):
    pass
    # return i[0] == actions_dict["RANGED_ATTACK"]
def is_block(i):
    return i == actions_dict.get("BLOCK")

class Node:
    def __init__(self, constants, turn, turn_number=1, parent=None, actions=[]):
        self.constants = constants

        self.q = 0
        self.n = 0

        self.turn_number = turn_number

        self.parent = parent
        self.turn = turn

        self.children = []

        self.actions = actions

    def get_actions(self):
        return self.actions

    def get_actions_functions(self):
        #Returns actions in a form that the game can actually use.
        #i.e. the PLAYER_MELEE_ATTACK, PLAYER_BLOCK and PLAYER_MOVE functions.
        actions_functions = [None for i in range(len(self.actions))]

        for i in range(len(self.actions)):
            if(is_melee_attack(self.actions[i])):
                actions_functions[i] = PLAYER_MELEE_ATTACK(self.actions[i][1:])
            elif(is_move(self.actions[i])):
                actions_functions[i] = PLAYER_MOVE(self.actions[i])
            else:
                actions_functions[i] = PLAYER_BLOCK(0)

        return actions_functions

    def get_parent_visits(self):
        return self.parent.get_visits()

    def get_turn_number(self):
        return self.turn_number

    def get_score(self):
        return self.q

    def get_visits(self):
        return self.n

    def get_child_nodes(self):
        return self.children

    def increment_visit(self):
        self.n += 1

    def increment_score(self):
        self.q += 1

    def add_score(self, score):
        self.q += score

    def decrement_score(self):
        self.q -= 1

    def expand_node(self):
        MELEE_ATTACK = actions_dict["MELEE_ATTACK"]
        # RANGED_ATTACK = actions_dict["RANGED_ATTACK"]

        MOVE_UP = actions_dict["MOVE_UP"]
        MOVE_DOWN = actions_dict["MOVE_DOWN"]
        MOVE_LEFT = actions_dict["MOVE_LEFT"]
        MOVE_RIGHT = actions_dict["MOVE_RIGHT"]

        BLOCK = actions_dict["BLOCK"]

        def generate_actions(turn, movement_points):
            #returns tuple of actions eg (0, (3, 2))
            #an integer represents moving/blocking
            #a tuple represents attacking
            player = turn.player

            actions_tuple = ()
            if(movement_points == 0):
                return ((),)

            if(movement_points == 1):
                for key, value in actions_dict.items():
                    if(value == actions_dict["MELEE_ATTACK"]):
                        for i in player.possible_melee_attack_coordinates_this_turn(turn.mapp):
                            actions_tuple += ((((value,) + i),),)
                        continue
                    actions_tuple += ((value,),)
                return actions_tuple

            lower_actions = generate_actions(turn, movement_points - 1)
            for i in lower_actions:
                if(is_melee_attack(i[-1]) or is_ranged_attack(i[-1]) or is_block(i[-1])):
                    #Don't continue appending actions if last action already instantly ends turn.
                    actions_tuple += (i,)
                    continue
                for key, value in actions_dict.items():
                    if(value == actions_dict["MELEE_ATTACK"]):
                        for j in player.possible_melee_attack_coordinates_this_turn(turn.mapp):
                            # actions_tuple += (i + ((value,) + j),)
                            actions_tuple += (i + ((value, j[0], j[1]),),)
                        continue
                    actions_tuple += (i + (value,),)
            return actions_tuple

            # for key, value in actions_dict.items():
            #     if(is_attack(value) or is_move(value)):
            #         actions_tuple +=

            #     lower_actions = generate_actions(movement_points - 1)
            #     print_debug(lower_actions)
            #     for i in lower_actions:
            #         actions_tuple += ((value,) + i,)
            # return actions_tuple

        print_debug(generate_actions(self.turn, self.constants.PLAYER_MOVEMENT_POINTS))

        print_debug("SELF:")
        self.print_info()
        print_debug()


        if(len(self.children) > 0):
            #Node is already fully expanded
            return

        for i in generate_actions(self.turn, self.constants.PLAYER_MOVEMENT_POINTS):
            #Instantly remove "useless actions", i.e. moving back and forth.
            is_useless = False
            for j in range(1, len(i)):
                if is_move(i[j-1]) and is_move(i[j]):
                    if(i[j-1] == MOVE_LEFT and i[j] == MOVE_RIGHT):
                        is_useless = True
                        break
                    if(i[j-1] == MOVE_RIGHT and i[j] == MOVE_LEFT):
                        is_useless = True
                        break
                    if(i[j-1] == MOVE_UP and i[j] == MOVE_DOWN):
                        is_useless = True
                        break
                    if(i[j-1] == MOVE_DOWN and i[j] == MOVE_UP):
                        is_useless = True
                        break
            if(is_useless):
                continue

            actions = [None for j in range(self.constants.PLAYER_MOVEMENT_POINTS)]
            for count in range(self.constants.PLAYER_MOVEMENT_POINTS):
                cur_action = i[count]
                print_debug("CURRENT_ACTION: {}".format(cur_action))
                if(is_block(cur_action)):
                    actions[count] = PLAYER_BLOCK(0)
                    break
                if(is_melee_attack(cur_action)):
                    actions[count] = PLAYER_MELEE_ATTACK(cur_action[1:])
                    break
                if(is_move(cur_action)):
                    print_debug("IS MOVE")
                    actions[count] = PLAYER_MOVE(i[count])
                    continue
            print_debug("Current position: " + str(self.turn.player.position))
            print_debug("Considering actions: " + str(i))

            cur_x, cur_y = self.turn.player.position
            prev_x, prev_y = self.turn.player.position
            is_valid = True

            #Temporary map to check stuff
            temp_mapp = copy.deepcopy(self.turn.mapp)
            temp_player = copy.deepcopy(self.turn.player)

            for count in range(self.constants.PLAYER_MOVEMENT_POINTS):
                if(count >= len(i)): break
                if(i[count] == BLOCK):
                    continue

                prev_x, prev_y = cur_x, cur_y

                if(i[count] == MOVE_UP):
                    cur_y -= 1
                if(i[count] == MOVE_LEFT):
                    cur_x -= 1
                if(i[count] == MOVE_RIGHT):
                    cur_x += 1
                if(i[count] == MOVE_DOWN):
                    cur_y += 1

                entity_at_target = self.turn.mapp.get_position((cur_x, cur_y))
                map_size = self.turn.mapp.size

                print_debug("{} : is_move(i[count]): {}".format(i[count], is_move(i[count])))
                print_debug("{} : is_melee_attack(i[count]): {}".format(i[count], is_melee_attack(i[count])))
                print_debug(i[count])
                if(is_move(i[count]) and (cur_x == map_size - 1 and cur_y == map_size - 1)):
                    print_debug("WIN!")
                    new_node = Node(self.constants, copy.deepcopy(self.turn), self.turn_number+1, self, i[:count+1])
                    new_node.turn.player.win = 1
                    self.children = [new_node]
                    return
                if(is_melee_attack(i[count])):
                    attack_coordinates = i[count][1:]
                    print_debug(attack_coordinates)
                    if(attack_coordinates not in temp_player.possible_melee_attack_coordinates_now(temp_mapp)):
                        print_debug(str(attack_coordinates) + " not in attack_coordinates...\n")
                        is_valid = False
                        break
                if(is_move(i[count]) and (cur_x < 0 or cur_y < 0)):
                    print_debug("Invalid; moving out of bounds at {}, {}\n".format(cur_x, cur_y))
                    is_valid = False
                    break
                if(is_move(i[count]) and (cur_x >= map_size or cur_y >= map_size)):
                    print_debug("Invalid; moving out of bounds at {}, {}\n".format(cur_x, cur_y))
                    is_valid = False
                    break
                if(is_move(i[count]) and not (entity_at_target is None)):
                    #Something's in the way
                    print_debug("Invalid; obstruction detected at {}, {}\n".format(cur_x, cur_y))
                    is_valid = False
                    break
                if(is_move(i[count]) and entity_at_target is None):
                    print_debug("Moving to {}, {}".format(cur_x, cur_y))
                    is_valid = True

                    temp_mapp.swap((prev_x, prev_y), (cur_x, cur_y))
                    temp_player.position = ((cur_x, cur_y))
                    # temp_mapp.print_array()

            if(not is_valid):
                continue
            new_node = Node(self.constants, self.turn.hypothetical_state(actions), self.turn_number + 1, self, i)
            print_debug("HYPOTHETHICAL POSITION:", end=''); print_debug(new_node.turn.player.position)
            print_debug("HYPOTHETHICAL ACTIONS:", end=''); print_debug(new_node.actions)
            # new_node.turn.mapp.print_array()
            print_debug()
            # new_node.turn.mapp.print_array()
            self.children += [new_node]
        print_debug("NUMBER OF CHILD NODES: " + str(len(self.children)))

        if(len(self.children) == 0):
            #This is so sad, let's just block.
            #i.e. no valid moves, block
            new_node = Node(self.constants, self.turn.hypothetical_state([PLAYER_BLOCK(0), None]), self.turn_number + 1, self, [-1, None])
            self.children = [new_node]

        self.print_children()

    def select_random_node(self):
        return random.choice(self.children)

    def select_best_node(self):
        print_debug("Expanding Nodes...")
        self.expand_node()
        print_debug("Expanded nodes!")

        uct_list = ([x.uct() for x in self.get_child_nodes()])
        max_uct = max(uct_list)
        if(max_uct == INFINITY):
            return self.select_random_node()
        max_uct_index = uct_list.index(max_uct)
        print_debug("BEST NODE: ", end=''); print_debug(self.get_child_nodes()[max_uct_index])
        return self.get_child_nodes()[max_uct_index]

    def select_best_visited_node(self):
        print_debug("Expanding Nodes...")
        self.expand_node()
        print_debug("Expanded nodes!")

        uct_list = ([x.deciding_uct() for x in self.get_child_nodes() if x.deciding_uct() < INFINITY])
        max_uct = max(uct_list)
        max_uct_list = ([x for x in self.get_child_nodes() if x.deciding_uct() == max_uct])
        # print_debug("BEST VISITED NODE: ", end=''); print_debug(self.get_child_nodes()[max_uct_index].get_actions())
        return random.choice(max_uct_list)
        # return self.get_child_nodes()[max_uct_index]

    def uct(self):
        if(self.get_visits() == 0):
            return INFINITY
        if(self.parent is None):
            return INFINITY
        return (self.get_score() / self.get_visits()) + (1.41 * math.sqrt(math.log(self.get_parent_visits()) / self.get_visits()))

        #Random multiplier added (from 1 to 1.2x)
        # return (self.get_score() / self.get_visits()) + (1.41 * math.sqrt(math.log(self.get_parent_visits()) / self.get_visits())) * (random.random() * 0.2 + 1)

    def deciding_uct(self):
        #Doesn't focus on exploration, used when deciding the absolute best node.
        if(self.get_visits() == 0):
            return INFINITY
        if(self.parent is None):
            return INFINITY

        if(is_melee_attack(self.actions[-1])):
            return 2 * ((self.get_score() / self.get_visits())) #+ (1.41 * math.sqrt(math.log(self.get_parent_visits()) / self.get_visits())))
        return (self.get_score() / self.get_visits()) #+ (1.41 * math.sqrt(math.log(self.get_parent_visits()) / self.get_visits()))

    def print_node(self, indent_level = 0):
        # uct_print_value = "INFINITY" if self.uct() == INFINITY else self.uct()
        # print_debug("\t" * indent_level + "{}, {}, q={},n={},uct={}".format(self.turn.player.position, self.actions, self.get_score(), self.get_visits(), uct_print_value))
        if(self.uct() == INFINITY):
            print_debug("\t" * indent_level + "{}, {}, n={}".format(self.turn.player.position, self.actions, self.get_visits()))
        else:
            print_debug("\t" * indent_level + "{}, {}, q={},n={},uct={}".format(self.turn.player.position, self.actions, self.get_score(), self.get_visits(), self.uct()))
        for i in self.children:
            i.print_node(indent_level + 1)

    def print_children(self):
        for i in self.children:
            i.print_info()
    def print_info(self):
        print_debug(self.actions)
        if(VERBOSE): self.turn.mapp.print_array()
        print_debug(self)

class MonteCarlo:
    def __init__(self, constants, turn):
        self.constants = constants

        initial_node = Node(constants,turn)
        self.initial_state = initial_node
        self.current_state = self.initial_state

        self.best_actions = []

    def get_initial_state(self):
        return self.initial_state

    def set_current_state(self, state):
        self.current_state = state

    def next_move(self):
        self.current_state = self.current_state.select_best_node()
        print_debug("CURRENT STATE: ",  end=''); print_debug(self.current_state)
        print_debug()

    def back_propogate_win(self):
        print_debug("BACKPROPAGATING...")
        while(not self.current_state is None):
            self.current_state.increment_visit()
            self.current_state.add_score(1 / self.current_state.get_turn_number())
            print_debug("CURRENT VISITS: " + str(self.current_state.get_visits()))
            print_debug("CURRENT SCORE: " + str(self.current_state.get_score()))
            self.current_state = self.current_state.parent

    def back_propogate_lose(self):
        print_debug("BACKPROPAGATING...")
        while(not self.current_state is None):
            self.current_state.increment_visit()
            # self.current_state.decrement_score()
            print_debug("CURRENT VISITS: " + str(self.current_state.get_visits()))
            print_debug("CURRENT SCORE: " + str(self.current_state.get_score()))
            self.current_state = self.current_state.parent

        print_debug("FINISHED BACKPROPAGATION!")

    def back_propogate_draw(self):
        #If after MAX_DEPTH and we still haven't won:
        #I'm not actually sure whether this will work
        print_debug("BACKPROPAGATING DRAW...")
        while(not self.current_state is None):
            self.current_state.increment_visit()

            self.current_state.add_score(1 / (2 * self.current_state.get_turn_number()))
            print_debug("CURRENT VISITS: " + str(self.current_state.get_visits()))
            print_debug("CURRENT SCORE: " + str(self.current_state.get_score()))
            self.current_state = self.current_state.parent

    def take_turn(self):
        import time
        start_time = time.time()

        while(time.time() - start_time < THINKING_TIME):
        # for i in range(1):
            # print_debug(time.time() - start_time)
            while(not self.current_state is None) and (not self.current_state.turn.check_game_over()):
                print_debug("TIME USED: " + str(time.time() - start_time))
                self.next_move()
                if(not self.current_state is None) and (self.current_state.turn_number > MAX_DEPTH):
                    #Time limit reached; back propagate a draw.
                    self.back_propogate_draw()
                    self.current_state = self.initial_state
                    break

            if(not self.current_state is None) and (self.current_state.turn.check_win()): #Game has ended
                self.back_propogate_win()
                self.set_current_state(self.get_initial_state())

            if(not self.current_state is None) and (self.current_state.turn.check_lose()):
                self.back_propogate_lose()

        self.best_actions = self.initial_state.select_best_visited_node().actions
        print_debug(self.initial_state.select_best_visited_node().actions)

    def print_node_tree(self):
        print_debug("\n")
        self.initial_state.print_node()
        print_debug("\t\t(end, end)")
        print_debug("\t(end, end)")


    def get_best_actions(self):
        return (self.best_actions)

    def get_best_actions_functions(self):
        return (self.initial_state.select_best_visited_node().get_actions_functions())


#TESTING
if(__name__ == '__main__'):
    constants = Constants()
    turn = Turn(5, 10, 10)
    # turn.mapp.print_array()
    # turn.set_preset([
    #     ["x", "x", "-", "-"],
    #     ["-", "o", "-", "-"],
    #     ["-", "-", "-", "-"],
    #     ["-", "-", "-", "a"],
    #     ])
    turn.set_preset([
        ["-", "o", "-", "#", "-"],
        ["-", "#", "-", "-", "-"],
        ["#", "#", "-", "#", "-"],
        ["-", "-", "-", "-", "#"],
        ["-", "#", "-", "-", "a"]
    ])

    # turn.set_preset([
    #     ["o", "-", "-", "#", "#"],
    #     ["-", "-", "-", "-", "-"],
    #     ["-", "-", "#", "#", "-"],
    #     ["-", "-", "#", "-", "-"],
    #     ["-", "-", "#", "-", "a"]
    # ])

#At the end, the AI returns a tuple ((action1), (action2))
    initial_node = Node(turn)
    # initial_node.expand_node()
    # initial_node = initial_node.select_best_visited_node()
# initial_node = initial_node.select_best_visited_node()
# initial_node = initial_node.select_best_visited_node()
# initial_node = initial_node.select_best_visited_node()
# initial_node = initial_node.select_best_visited_node()
# print_debug(initial_node.turn.check_game_over())
# initial_node = initial_node.select_best_visited_node()
# print_debug(initial_node.turn.check_game_over())

    mcts = MonteCarlo(initial_node)
    mcts.take_turn()

    mcts.print_node_tree()

    print_debug(mcts.get_best_actions())
    print_debug(mcts.get_best_actions_functions())

# import time
# start_time = time.time()

# while(time.time() - start_time < THINKING_TIME):
#     while(not mcts.current_state is None) and (not mcts.current_state.turn.check_game_over()):
#         mcts.next_move()

#     if(not mcts.current_state is None) and (mcts.current_state.turn.check_win()): #Game has ended
#         mcts.back_propogate_win()
#         mcts.set_current_state(mcts.get_initial_state())

#     if(not mcts.current_state is None) and (mcts.current_state.turn.check_lose()):
#         mcts.back_propogate_lose()

# print_debug(mcts.initial_state.select_best_visited_node().get_score())
# print_debug(mcts.initial_state.select_best_visited_node().turn.mapp.print_array())
