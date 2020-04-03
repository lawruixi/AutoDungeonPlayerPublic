import json
import copy

toggle_Debug_Prints = False
class Constants():
    STANCE_DEFAULT = 0
    STANCE_ATTACK = 1
    STANCE_BLOCK = 2
    MOVE_LEFT = 0
    MOVE_UP = 1
    MOVE_RIGHT = 2
    MOVE_DOWN = 3
    PLAYER_MOVE = lambda z: (lambda x,y: x.move(z,y))
    PLAYER_MELEE_ATTACK = lambda z: (lambda x,y: x.attack_melee(z,y))
    PLAYER_RANGED_ATTACK = lambda z: (lambda x,y: x.attack_ranged(z,y))
    PLAYER_BLOCK = lambda z: (lambda x,y: x.block())

    def __init__(self):
        return

    #game instances
    def custom_game(self,AI_move_pts,AI_hp,AI_attk,AI_move,player_move_pts,player_hp,player_attk,player_move,player_ranged_attack,player_min_ranged_range,player_ranged_range):
        """
        Create custom stats for game:
        Input in this order:
        AI_MOVEMENT_POINTS, AI_HEALTH, AI_ATTACK, AI_MOVEMENT, PLAYER_MOVEMENT_POINTS, PLAYER_HEALTH, PLAYER_ATTACK, PLAYER_MOVEMENT
        """
        self.AI_MOVEMENT_POINTS = AI_move_pts
        self.AI_HEALTH = AI_hp
        self.AI_ATTACK = AI_attk
        self.AI_MOVEMENT = AI_move
        self.PLAYER_MOVEMENT_POINTS = player_move_pts 
        self.PLAYER_MELEE_ATTACK_DMG = player_attk
        self.PLAYER_HEALTH = player_hp
        self.PLAYER_MOVEMENT = player_move
        self.PLAYER_RANGED_ATTACK_DMG = player_ranged_attack
        self.PLAYER_RANGED_RANGE = player_ranged_range
        self.PLAYER_MIN_RANGED_RANGE = player_min_ranged_range


class Thing:
    Passable = False
    Pushable = False
    initialTestPassable = True
    def __init__(self,Passable, Pushable,initialTestPassable):
        self.Passable = Passable
        self.Pushable = Pushable
        self.initialTestPassable = initialTestPassable

class Wall(Thing):
    def __init__(self):
        super().__init__(False,False,False)

class GoalObject(Thing):
    def __init__(self):
        super().__init__(True,False,True)

class Character(Thing):
    """

    Args:
        health int: health
        attack int: attack damage
        movement int: movement speed (dictates turn order)
        movement_points int: number of actions left
        position tup: tuple consisting of x and y coordinates of position
        stance int: stores stance constant, dictating certain actions

    """
    def __init__(self,position,constants):
        super().__init__(False,False,True)
        self.constants = constants
        self.health = self.constants.AI_HEALTH
        self.attack_dmg_melee = self.constants.AI_ATTACK
        self.movement = self.constants.AI_MOVEMENT
        self.stance = self.constants.STANCE_DEFAULT
        self.movement_points = self.constants.AI_MOVEMENT_POINTS
        self.position = position

    def take_damage(self,dmg,mapp):
        """
        Internal Function to take damage
        Args:
            int dmg: dmg to be taken
            Map mapp: map object
        """
        self.health-=dmg
        if self.health<=0:
            mapp.replace_object(self.position,None)

    def set_stance(self,stance):
        self.stance = stance

    def get_stance(self):
        return self.stance

    def move(self,direction,mapp):
        """
        Moves character in the direction given (check constants)
        Returns True if move is successful
        Returns False if there is an error (object in the way)

        Args:
            direction int: 0 is left, 1 is up, 2 is right, 3 is down
            Map mapp: Map object

        """
        a = mapp.check_move(self.position,direction)
        if a == "Win":
            return "Win"
        if  a == True:
            new_position = mapp.get_new_position_from_direction(self.position,direction)
            self.movement_points-=1
            mapp.swap(self.position,new_position)
            self.position = new_position
            return True
        else:
            self.movement_points -= 1
        return False

    def block(self):
        """
        Blocks the next attack, just call.
        """
        self.set_stance(self.constants.STANCE_BLOCK)
        self.movement_points = 0

    def deal_damage_by_attacking(self,enemy,mapp,dmg):
        """
        Function to deal damage to enemy
        Returns false if enemy is already dead and can't be attacked
        Args:
            Character enemy: enemy that will be attacked
            Map mapp: map object the game takes place in.
        """
        if enemy.health <=0:
            return False

        self.set_stance(self.constants.STANCE_ATTACK)
        self.movement_points=0
        if(enemy.get_stance == self.constants.STANCE_BLOCK):
            enemy.set_stance(self.constants.STANCE_DEFAULT)
        enemy.take_damage(dmg,mapp)
        return True

    def attack_melee(self,position,mapp):
        """
        Args:
            direction int: 0 is left, 1 is up, 2 is right, 3 is down
            Map mapp: Map object

        """

        if position in self.possible_melee_attack_coordinates_now(mapp):
            if isinstance(mapp.get_position(position),Character):
                a = self.deal_damage_by_attacking(mapp.get_position(position),mapp,self.attack_dmg_melee)
                return a
        #error handling
        if position not in self.possible_melee_attack_coordinates_now(mapp):
            print("Invalid attack position of "+str(position))
        return False
    def possible_melee_attack_coordinates_now(self,mapp):
        lst = []
        for x in range(2):
            for y in range(2):
                if (x == 0 and y == 0):
                    continue
                if (x+y>1):
                    continue
                temppos = (self.position[0]-x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]-x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
        return lst

    def possible_melee_attack_coordinates_this_turn(self,mapp):
        lst = []
        for x in range(1+self.constants.PLAYER_MOVEMENT_POINTS):
            for y in range(1+self.constants.PLAYER_MOVEMENT_POINTS):
                if (x == 0 and y == 0):
                    continue
                temppos = (self.position[0]-x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]-x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
        return lst

    def parse_string(self,string):
        # a = string.split()
        # tempx = 0
        # tempy = 0
        # for i in range(1,len(a),2):
        #     if i == 1:
        #         self.health = int(a[i])
        #     elif i == 3:
        #         self.attack = int(a[i])
        #     elif i == 5:
        #         self.movement = int(a[i])
        #     elif i == 7:
        #         self.movement_points = int(a[i])
        #     elif i==9:
        #         tempx = int(a[i])
        #     elif i == 11:
        #         tempy = int(a[i])
        #         self.position = (tempx,tempy)
        json_dict = json.loads(string)
        self.health = json_dict["Health"]
        self.attack = json_dict["Attack"]
        self.movement = json_dict["Movement"]
        self.movement_points = json_dict["Movement_Pts"]
        tempx = json_dict["pos_x"]
        tempy = json_dict["pos_y"]
        self.position = (tempx, tempy)

    def __str__(self):
        # return "Health "+str(self.health)+" Attack "+str(self.attack)+" Movement "+str(self.movement)+" Movement_Pts "+str(self.movement_points)+" pos_x "+str(self.position[0])+" pos_y "+str(self.position[1])
        # return "Health: {0}"
        json_dict = {
            "Health": self.health,
            "Melee Attack": self.attack_dmg_melee,
            "Movement": self.movement,
            "Movement_Pts": self.movement_points,
            "pos_x": self.position[0],
            "pos_y": self.position[1]
        }
        return json.dumps(json_dict)

class Player(Character):

    def __init__(self,position,constants):
        super().__init__(position,constants)
        self.health = self.constants.PLAYER_HEALTH
        self.attack_dmg_melee = self.constants.PLAYER_MELEE_ATTACK_DMG
        self.movement = self.constants.PLAYER_MOVEMENT
        self.movement_points = self.constants.PLAYER_MOVEMENT_POINTS
        self.win = 0
        self.attack_dmg_ranged = self.constants.PLAYER_RANGED_ATTACK_DMG
        self.attack_range_ranged = self.constants.PLAYER_RANGED_RANGE
        self.attack_min_range_ranged = self.constants.PLAYER_MIN_RANGED_RANGE

    def move(self,direction,mapp):
        a = super().move(direction,mapp)
        if a == "Win":
            self.win = 1

    def attack_ranged(self,attack_position,mapp):
        x = self.position[0] - attack_position[0]
        y = self.position[1] - attack_position[1]

        if (abs(x)+abs(y))<self.constants.PLAYER_RANGED_RANGE:
            if isinstance(mapp.get_position(attack_position),Character):
                return self.deal_damage_by_attacking(mapp.get_position(attack_position),mapp,self.attack_dmg_ranged)
        return False

    def possible_ranged_attack_coordinates_now(self,mapp):
        lst = []
        for x in range(self.attack_min_range_ranged,self.attack_range_ranged+1):
            for y in range(self.attack_min_range_ranged,self.attack_range_ranged+1):
                
                if (x == 0 and y == 0):
                    continue
                if (x+y>self.attack_range_ranged):
                    continue
                temppos = (self.position[0]-x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
                temppos = (self.position[0]-x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        if temppos not in lst:
                            lst.append(temppos)
        return lst


    def possible_ranged_attack_coordinates_this_turn(self,mapp):
        lst = []
        for x in range(self.attack_min_range_ranged,self.attack_range_ranged+self.constants.PLAYER_MOVEMENT_POINTS):
            for y in range(self.attack_min_range_ranged,self.attack_range_ranged+self.constants.PLAYER_MOVEMENT_POINTS):
                
                if (x == 0 and y == 0):
                    continue
                if (x+y>self.attack_range_ranged):
                    continue
                temppos = (self.position[0]-x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        lst.append(temppos)
                temppos = (self.position[0]+x,self.position[1]-y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        lst.append(temppos)
                temppos = (self.position[0]-x,self.position[1]+y)
                if mapp.check_is_in_map(temppos):
                    if isinstance(mapp.get_position(temppos),Character):
                        lst.append(temppos)
        return lst


    
    def __str__(self):
        # return "Health "+str(self.health)+" Attack "+str(self.attack)+" Movement "+str(self.movement)+" Movement_Pts "+str(self.movement_points)+" pos_x "+str(self.position[0])+" pos_y "+str(self.position[1])
        # return "Health: {0}"
        json_dict = {
            "Health": self.health,
            "Melee Attack": self.attack_dmg_melee,
            "Ranged Attack": self.attack_dmg_ranged,
            "Ranged Range": self.attack_dmg_ranged,
            "Movement": self.movement,
            "Movement_Pts": self.movement_points,
            "pos_x": self.position[0],
            "pos_y": self.position[1]
        }
        return json.dumps(json_dict)
