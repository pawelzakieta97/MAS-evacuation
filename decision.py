from collections import OrderedDict
from heapq import heappop, heappush
from building import *

class DecisionEngine:
    def __init__(self, world, building: Building, agent_type='leader'):
        self.world = world
        self.building = building
        self.agent_type = agent_type

        # KNOWLEDGE[room]:
        # 0 -   No information about a room, a follower only knows there is a
        #       room that theoretically might lead to an exit. During the
        #       search for the closest exit, it is treated as an exit with very
        #       high cost (will be explored if no other way is available)
        # 1 -   The agent knows what doorways are available from this room.
        # 2 -   The agent knows the room is dangerous. This means that this
        #       room will be excluded from graph search. Agents know the room
        #       is dangerous once they get to any adjacent room (thus they will
        #       never enter a dangerous room)
        self.knowledge = {}
        if agent_type == 'follower':
            for room in building.rooms:
                self.knowledge[room] = 0
        if agent_type == 'leader':
            for room in building.rooms:
                self.knowledge[room] = 1

    def observation(self, agents):
        """

        :param agents:
        :return:
        """

    def get_path(self, current_room: Room):
        UNKNOWN_COST = 1000
        def get_cost(doorway: Doorway, room: Room):
            if room.is_outside:
                return 0
            elif self.knowledge[room] == 1:
                return doorway.distance
            elif self.knowledge[room] == 0:
                return UNKNOWN_COST
            return None
        opened = {}
        considered = []
        s = (0, current_room)
        heappush(considered, s)
        while not s[1].is_outside and self.knowledge[s[1]] > 0:
            if len(considered):
                s = heappop(considered)
                while s[1] in opened.keys():
                    s = heappop(considered)
            else:
                print('no exit')
                return
            adjacent_rooms = s[1].get_adjacent_rooms()
            for doorway, room in adjacent_rooms.items():
                if room not in opened.keys():
                    cost = get_cost(doorway, room)
                    if cost is not None:
                        heappush(considered, (s[0]+cost, room))
            if s[1] not in opened.keys():
                opened[s[1]] = s[0]
            # print(s[1], s[0])

        path = [s]
        while path[0][1] != current_room:
            adjacent_rooms = path[0][1].get_adjacent_rooms()
            for doorway, room in adjacent_rooms.items():
                cost = get_cost(doorway, room)
                if cost is not None:
                    if room in opened.keys() and room not in [element[1] for element in path]\
                            and abs(opened[room] - (path[0][0] - cost))< 0.001:
                        path.insert(0, (opened[room], room))
                        break
        return path


if __name__ == '__main__':

    d1 = Doorway((0,0))
    d2 = Doorway((10,0))
    d3 = Doorway((20,0))
    d4 = Doorway((30,0))
    r1 = Room(doorways=[d1, d3], walls=[], name='1')
    r2 = Room(doorways=[d1, d2], walls=[], name='2')
    r3 = Room(doorways=[d2], walls=[], name='3')
    r4 = Room(doorways=[d3, d4], walls=[], name='4')
    r4.is_dangerous = True
    building = Building(rooms=[r1,r2,r3,r4], doorways=[d1,d2,d3,d4])
    de = DecisionEngine(world=None, building=building)
    # de.knowledge[r4] = 2
    path = de.get_path(r1)
    print([element[1].name for element in path])


    # d1 = Doorway((0,0))
    # d2 = Doorway((10,0))
    # d3 = Doorway((20,0))
    # d4 = Doorway((30,0))
    # d5 = Doorway((40,0))
    # r1 = Room(doorways=[d1, d2], walls=[], name='1')
    # r2 = Room(doorways=[d1, d3], walls=[], name='2')
    # r3 = Room(doorways=[d2, d3, d4], walls=[], name='3')
    # r4 = Room(doorways=[d4, d5], walls=[], name='4')
    #
    # building = Building(rooms=[r1,r2,r3,r4], doorways=[d1,d2,d3,d4, d5])
    # de = DecisionEngine(world=None, building=building)
    # # de.knowledge[r4] = 2
    # de.get_path(r1)
