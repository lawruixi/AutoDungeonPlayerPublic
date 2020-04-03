#gamelogic stuff
import random
import copy
from classes_functions_game_objects import *




class Turn():
    def __init__(self,size,wall_chance,enemy_count,constants):
        self.constants = constants
        self.mapp = Map(size,wall_chance,enemy_count,self.constants)
        self.characters = self.mapp.get_characters()
        self.current = self.characters[0]
        self.player = None
        for i in self.characters:
            if isinstance(i,Player):
                self.player = i
        self.current_counter = 0
        self.dead_counter = 0
        self.player_dead = 0
        self.win = 0
        self.lose = 0

    def reset_stances(self):
        for i in self.characters:
            i.set_stance(self.constants.STANCE_DEFAULT)

    def reset_stance(self,char):
        char.set_stance(self.constants.STANCE_DEFAULT)

    def reset_movement_points(self):
        for i in self.characters:
            if i.health>0:
                if isinstance(i,Player):
                    i.movement_points = self.constants.PLAYER_MOVEMENT_POINTS
                else:
                    i.movement_points = self.constants.AI_MOVEMENT_POINTS
            else:
                i.movement_points = 0

    def determine_action_sequence(self):
        self.characters = sorted(self.characters, key = lambda x: x.movement,reverse=True)
        return self.characters

    def check_end_turn(self):
        if self.current_turn().movement_points <= 0:
            self.current_counter += 1
            self.current_counter%=len(self.characters)
            if self.current_counter == 0:
                self.reset_movement_points()
                #self.reset_stances()
            return True
        return False

    def check_is_dead(self,char):
        if (char.health<=0):
            if isinstance(char,Player):
                self.player_dead+=1
            else:
                self.dead_counter+=1
            self.characters.remove(char)
            self.current_counter%=len(self.characters)
            if self.current_counter == 0:
                self.reset_movement_points()
                self.reset_stances()
            return True
        return False

    def current_turn(self):
        return self.characters[self.current_counter]

    def check_game_over(self):
        if self.lose == 1:
            return True
        if not (self.player in self.characters):
            return True
        if ((self.check_is_dead(self.player) == 1) or (self.player.win == 1) or (self.player_dead == 1)):
            return True
        return False

    def check_win(self):
        if (self.player.win == 1):
            self.win = 1
        return self.player.win == 1

    def check_lose(self):
        if not (self.player in self.characters):
            self.lose = 1
            return True
        if self.check_is_dead(self.player) or self.player_dead == 1:
            self.lose = 1
        return self.check_is_dead(self.player) or self.player_dead == 1

    def set_preset(self,text_map):
        """
        Set map based of input
        Args:
            2d String array: text_map
        Example:
        [["o","-","-"],["#","-","-"],["x","-","a"]]
        """
        self.mapp.map_GUI = text_map
        self.mapp.mapp = self.mapp.parse_string_map_array()
        self.mapp.size = len(self.mapp.mapp[0])
        self.characters = self.mapp.get_characters()
        self.current = self.characters[0]
        self.player = None
        for i in self.characters:
            if isinstance(i,Player):
                self.player = i
        self.current_counter = 0
        self.dead_counter = 0
        self.player_dead = 0
        self.win = 0

    def hypothetical_state(self,actions):
        new_turn = copy.deepcopy(self)
        a = new_turn.characters
        stop_char = new_turn.current_turn()
        stop = False
        for b in range(len(a)):
            i = new_turn.current_turn()
            if i == stop_char and stop == True:
                break
            elif i == stop_char:
                stop = True

            while True:
                if new_turn.check_is_dead(i):
                    break
                elif new_turn.check_end_turn():
                    break
                elif (not isinstance(i,Player)) and isinstance(i,Character):
                    for c in range(self.constants.AI_MOVEMENT_POINTS):
                        dumb_ai(i,new_turn.mapp)
                        if i.movement_points == 0:
                            break
                elif isinstance(i,Player):
                    for c in range(self.constants.PLAYER_MOVEMENT_POINTS):
                        actions[c](i,new_turn.mapp)
                        if new_turn.check_win():    
                            new_turn.win = 1
                            return new_turn
                        if i.movement_points == 0:
                            break
                    #player move
        return new_turn

class Map():
    """
    Args:
        2d Array Map: takes in 2d array of game map in initial state (game_objects map).
    """
    def __init__(self,size,wall_chance,enemy_count,constants):
        """
        Generates new map of size size
        Player spawns in top left, goal spawns in bottom right.
        Args:
            int size: size of map (n x n)
            float wall_chance: chance of wall
            int enemy_count: Number of enemies
        """
        self.constants = constants
        self.map_GUI = self.generate_map_array(size,wall_chance,enemy_count)
        self.mapp = self.parse_string_map_array()
        self.size = size

    def get_characters(self):
        """
        returns all characters on map currently
        """
        g = []
        for row in self.mapp:
            for z in row:
                if isinstance(z,Character):
                    g.append(z)
        return g

    def is_passable(self,position):
        """
        Returns if coordinate is passible or not
        (Returns false if not on map)
        """
        if not self.check_is_in_map(position):
            return False

        x = self.mapp[position[1]][position[0]]
        if isinstance(x,Thing):
            return x.Passable
        return True

    def is_init_passable(self,position):
        """
        Returns if coordinate is passible or not
        (Returns false if not on map)
        """
        if not self.check_is_in_map(position):
            return False

        x = self.mapp[position[1]][position[0]]
        if isinstance(x,Thing):
            return x.initialTestPassable
        return True

    def swap(self,original_position,new_position):
        """
        swaps objects at inputted positions, includes nones
        Args:
            Tuple (x,y): pos1
            Tuple (x,y): pos2
        """

        x,y = self.mapp[original_position[1]][original_position[0]],self.mapp[new_position[1]][new_position[0]]
        self.mapp[original_position[1]][original_position[0]],self.mapp[new_position[1]][new_position[0]] = y,x

    def check_is_in_map(self,position):
        """
        Check if coordinate is in map
        """

        if (position[1]>=self.size or position[0]>=self.size or position[1]<0 or position[0]<0) :
            return False
        return True

    def get_position(self,position):
        """
        Returns object at that coordinate
        If nothing is there returns None
        if not in map returns False
        """
        if not self.check_is_in_map(position):
            return False

        return self.mapp[position[1]][position[0]]

    def update_GUI_map(self):
        """
        Updates textmap
        """
        self.map_GUI = self.parse_object_map_array()

    def replace_object(self,position,new_thing):
        """
        replaces object at inputted position.
        Returns true if successful,
        false if fail (not in map)
        """
        if not self.check_is_in_map(position):
            return False
        self.mapp[position[1]][position[0]] = new_thing
        return True

    def get_GUI_map(self):
        """
        Returns text map
        """
        self.update_GUI_map()
        return self.map_GUI

    def get_object_map(self):
        return self.mapp

    def generate_map_array(self,size,wall_chance,enemy_count):
        """

        Generates square map array of length size and returns generated map.
        Player is guranteed to spawn in the top left corner, and goal is guranteed to be in the bottom right corner.

        Args:
            size int: Map size.
            wall_chance float: Chance to spawn wall
            enemy_count int: Number of enemies
        """
        grid = [ [0 for x in range(size)] for x in range(size)]
        for i in range(size):
            for z in range(size):
                q = random.random()
                if q <wall_chance:
                    grid[i][z] = "#"
                else:
                    grid[i][z] = "-"
        grid[0][0] = "o"
        grid[-1][-1] = "a"

        while enemy_count>0:
            for i in range(size):
                if enemy_count == 0:
                    break
                for z in range(size):
                    if grid[i][z] == "-":
                        if random.randrange(0,10) == 0 and enemy_count>0:
                            enemy_count-=1
                            grid[i][z] = "x"
                            if enemy_count == 0:
                                break

        return grid

    def print_array(self):
        """
        Prints the map
        """
        self.update_GUI_map()
        for x in self.map_GUI:
            print(" ".join([str(y) for y in x]))

    def parse_string_map_array(self):
        """

        Parses map array and returns array of objects.


        """

        #O -> Player
        ## -> Wall
        #X -> Enemy
        #A -> Exit
        #- -> None

        arr = self.map_GUI
        rows = len(arr)
        columns = len(arr[0])

        object_arr = [[None for i in range(columns)] for j in range(rows)]

        for i in range(rows):
            for j in range(columns):
                value = arr[i][j]
                value = value.strip().lower()

                if(value == "o"):
                    player = Player((j,i),self.constants)
                    object_arr[i][j] = player
                elif(value == "#"):
                    wall = Wall()
                    object_arr[i][j] = wall
                elif(value == "x"):
                    enemy = Character((j,i),self.constants)
                    object_arr[i][j] = enemy
                elif(value == "a"):
                    goal = GoalObject()
                    object_arr[i][j] = goal
                else:
                    object_arr[i][j] = None
        return object_arr

    def parse_object_map_array(self):

        """

        Basically same thing as parse_string_map_array, but the other way around.

        Args:
            arr Thing[]: The object arr to be parsed.
        """
        arr = self.mapp
        rows = len(arr)
        columns = len(arr[0])

        string_arr = [["-" for i in range(columns)] for j in range(rows)]

        for i in range(rows):
            for j in range(columns):
                value = arr[i][j]

                if(value is None):
                    string_arr[i][j] = "-"
                elif(isinstance(value, Player)):
                    string_arr[i][j] = "o"
                elif(isinstance(value, Wall)):
                    string_arr[i][j] = "#"
                elif(isinstance(value, Character)):
                    string_arr[i][j] = "x"
                elif(isinstance(value, GoalObject)):
                    string_arr[i][j] = "a"

        return string_arr

    def check_move(self,position,direction):
        new_position = self.get_new_position_from_direction(position,direction)
        if new_position!=None:
            if not self.is_passable(new_position):
                return False
            if isinstance(self.get_position(new_position),GoalObject):
                return "Win"
            return True
        return False

    def check_move_initial(self,position,direction):
            new_position = self.get_new_position_from_direction(position,direction)
            if new_position!=None:
                if not self.is_init_passable(new_position):
                    return False
                if isinstance(self.get_position(new_position),GoalObject):
                    return "Win"
                return True
            return False

    def get_new_position_from_direction(self,position,direction):
        new_position = None
        if direction == self.constants.MOVE_LEFT and position[0]>0:
            new_position = (position[0]-1,position[1])
        if direction == self.constants.MOVE_DOWN and position[1]<self.size-1:
            new_position = (position[0],position[1]+1)
        if direction == self.constants.MOVE_UP and position[1]>0:
            new_position = (position[0],position[1]-1)
        if direction == self.constants.MOVE_RIGHT and position[0]<self.size-1:
            new_position = (position[0]+1,position[1])
        return new_position
#Output functions


def dumb_ai(char,mapp):
    """
    If player is in 2 tile radius, move to them
    If player is next to char, attack
    else move randomly
    Args:
        Character char: character that is controlled by the dumb ai
        Map mapp: The map that the game is being played on.
    """
    current_position = char.position
    for i in range(-3,4):
        for z in range(-3,4):
            temp_pos = (current_position[0]+i,current_position[1]+z)
            if (isinstance(mapp.get_position(temp_pos),Player) and not mapp.get_position == None and not mapp.get_position == False):
                if (i == 0 and abs(z) == 1) or (abs(i) == 1 and z == 0):
                    if toggle_Debug_Prints:
                        print("AI is trying to attack" + str(temp_pos))
                    #char.movement_points = 0
                    return char.attack_melee(temp_pos,mapp)
                movement_sequence = (generate_movement(char.position,mapp,temp_pos,[],[]))
                if movement_sequence[0]:
                    if toggle_Debug_Prints:
                        print("AI is trying to move to the player in the direction of "+str(movement_sequence))
                    return char.move(movement_sequence[1][0],mapp)
    else:
        possibilities = [0,1,2,3]
        while True and len(possibilities)>0:
            picker = random.randrange(0,len(possibilities))
            if mapp.check_move(char.position,possibilities[picker]) == True:
                char.move(possibilities[picker],mapp)
                if toggle_Debug_Prints:
                    print("AI is trying to move randomly in the direction of "+str(possibilities[picker]))
                return True
            possibilities.remove(possibilities[picker])
        if toggle_Debug_Prints:
            print("AI is stuck!")
        char.movement_points = 0
        return False

def generate_movement(pos,mapp,move_to,closed_list,open_list,initial = False):
    """
    Employs A* pathfinding method to find path to target location (move_to) from current location (pos)
    on a given map (mapp)

    Args:
        tuple pos: coordinate tuple of current position to move from
        Map mapp
        tuple move_to: coordinate tuple of target position
    """
    closed_list.append(pos)
    for i in range(4):
        if initial:
            if mapp.check_move_initial(pos,i):
                coord = mapp.get_new_position_from_direction(pos,i)
                if coord == move_to:
                    return (True,[i])
                if coord in closed_list:
                    pass
                else:
                    A_score = abs(pos[0]-coord[0])+abs(pos[1]-coord[1])
                    B_score = abs(move_to[0]-coord[0])+abs(move_to[1]-coord[1])
                    F_score = A_score+B_score
                    open_list.append((F_score,coord,i)) 
        elif mapp.check_move(pos,i):
            coord = mapp.get_new_position_from_direction(pos,i)
            if coord == move_to:
                return (True,[i])
            if coord in closed_list:
                pass
            else:
                A_score = abs(pos[0]-coord[0])+abs(pos[1]-coord[1])
                B_score = abs(move_to[0]-coord[0])+abs(move_to[1]-coord[1])
                F_score = A_score+B_score
                open_list.append((F_score,coord,i))
    test_case = (False,[])
    while test_case[0] == False:
        if len(open_list) == 0:
            return (False,[])
        open_list.sort()
        open_list.reverse()
        #print(open_list,pos)
        next_check = open_list.pop()
        open_list.reverse()
        test_case = generate_movement(next_check[1],mapp,move_to,closed_list,[],initial)
    a = [next_check[2]]+test_case[1]
    return (True,a)