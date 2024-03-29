from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random
import path_finding

__pragma__('iconv')
__pragma__('tconv')
#__pragma__('opov')


# don't try to use global variables!!

class MyRobot(BCAbstractRobot):

    round = -1

    initial_pilgrims = 1
    initial_crusaders = 1
    spawnloc = None

    surrounding_tiles = [
        [-1, -1],  # Top-Left
        [0, -1],  # Top
        [1, -1],  # Top-Right
        [1, 0],  # Right
        [1, 1],  # Bottom-Right
        [0, 1],  # Bottom
        [-1, 1],  # Bottom-Left
        [-1, 0]  # Left
    ]

    destination = None
    destination_path = None

    def get_closest_resource(self, m, x, y):  # Gives x,y of closest resource
        loc = (x, y)
        closest_loc = (-1, -1)
        best_dist_sq = 64 * 64 + 64 * 64 + 1
        for x in range(len(m)):
            if (x - loc[0])**2 > best_dist_sq:
                continue
            for y in range(len(m[0])):
                if (y - loc[1])**2 > best_dist_sq:
                    continue
                d = (x-loc[0]) ** 2 + (y-loc[1]) ** 2
                if m[y][x] and d < best_dist_sq:
                    best_dist_sq = d
                    closest_loc = (x,y)
        return closest_loc

    # moves "smartly" to [x,y]. Make sure [x,y] is passable
    def move_to(self, passable_map, visible_map):
        y = self.me.y
        x = self.me.x
        if(x == self.destination[0] and y==self.destination[1]):
            return None
        for i in range(len(self.destination_path)-1, -1, -1):
            x1, y1 = self.destination_path[i]
            if(passable_map[y][x] and visible_map[y][x] == 0 and (x-x1)**2+(y-y1)**2 <= SPECS['UNITS'][self.me.unit()]['SPEED']):
                return self.move(x1-x, y1-y)

    def get_path(self,x,y,passable_map): #returns path to [x,y], tile by tile
        return path_finding.astar(passable_map,[self.me.y,self.me.x],[y,x])

    def in_map(self, x, y, n):
        if(x >= 0 and y >= 0 and x < n and y < n):
            return True
        return False

    def is_adjacent(self, r):  # Returns true if 'r' object is adjacent to 'self' object
        l = [r.x-self.me.x, r.y-self.me.y]
        for i in self.surrounding_tiles:
            if(l == i):
                return True
        return False

    def turn(self):
        attackable = []
        passable_map = self.get_passable_map()
        karbonite_map = self.get_karbonite_map()
        visible_map = self.get_visible_robot_map()
        fuel_map = self.get_fuel_map()
        visible_robots = self.get_visible_robots()

        if self.spawnloc is None:
            # first turn!
            self.spawnloc = (self.me.x, self.me.y)

        for r in visible_robots:
            if not self.is_visible(r):
                continue
            dist = (r.x - self.me.x)**2 + (r.y - self.me.y)**2
            if r.team != self.me.team and SPECS['UNITS'][SPECS["CRUSADER"]]['ATTACK_RADIUS'][0] <= dist <= SPECS['UNITS'][SPECS["CRUSADER"]]['ATTACK_RADIUS'][1]:
                attackable.append(r)
            if r.team == self.me.team and r.unit == SPECS['CASTLE']:
                if self.me.karbonite > 0 or self.me.fuel > 0 and dist < 3.5:
                    return self.give(r.x - self.me.x, r.y - self.me.y, self.me.karbonite, self.me.fuel)

        if self.me['unit'] == SPECS['CASTLE']:

            self.log("Castle")
            for dx, dy in self.surrounding_tiles:
                x = self.me.x+dx
                y = self.me.y+dy
                if(self.in_map(x,y,len(passable_map)) and passable_map[y][x] == True and visible_map[y][x] == 0):
                    if(self.initial_pilgrims > 0):
                        self.log("Created pilgrim.")
                        self.initial_pilgrims -= 1
                        return self.build_unit(SPECS['PILGRIM'], dx, dy)
                    elif(self.initial_crusaders > 0):
                        self.log("Created crusader.")
                        self.initial_crusaders -= 1
                        return self.build_unit(SPECS['CRUSADER'], dx, dy)

        elif self.me['unit'] == SPECS['PILGRIM']:
            self.log("Pilgrim:")
            if self.destination is None:
                self.destination = self.get_closest_resource(karbonite_map, self.me.x, self.me.y)

            if self.destination_path is None:
                self.destination_path = self.get_path(*self.destination, passable_map)
                self.log("Found path.")

            if self.me.karbonite == SPECS['UNITS'][SPECS["PILGRIM"]]['KARBONITE_CAPACITY']:
                for r in visible_robots:
                    if(r.team == self.me.team and r.id == SPECS['CRUSADER'] and self.is_adjacent(r)):
                        return self.give(r.x-self.me.x, r.y-self.me.y, self.me.karbonite, 0)

            if(self.me.x == self.destination[0] and self.me.y == self.destination[1]):
                return self.mine()
            else:
                move = self.move_to(*self.destination, passable_map, visible_map)
                if(move is not None):
                    return move

        elif self.me['unit'] == SPECS["CRUSADER"]:
            self.log("Crusader")
            if attackable:
                r = attackable[0]
                self.log('attacking! ' + ' at loc ' +
                         (r.x - self.me.x, r.y - self.me.y))
                return self.attack(r.x - self.me.x, r.y - self.me.y)

            if self.destination is None:
                if self.me.karbonite is SPECS['UNITS'][SPECS["CRUSADER"]]['KARBONITE_CAPACITY']:
                    self.destination = self.spawnloc
                else:
                    self.destination = self.get_closest_resource(karbonite_map, self.spawnloc[0], self.spawnloc[1])
            move = self.move_to(*self.destination, passable_map, visible_map)
            if(move is not None):
                return move

robot = MyRobot()
