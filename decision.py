import random
from collections import OrderedDict
from heapq import heappop, heappush
from building import *
from typing import List
from distance import distance
from model import Model

class DecisionEngine:
    def __init__(self, model, agent, rationality=None):
        self.model = model
        self.agent = agent
        self.wkurfactor = 0
        if rationality is None:
            self.rationality = 0.1+random.random()*0.8
        else:
            self.rationality = rationality
        # self.rationality = 0.1
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
        # 3 -   Clogged doorway
        self.knowledge = {}
        if self.agent.type == 'follower':
            path = self.entry_path([self.agent.current_room])
            for room in model.building.rooms:
                self.knowledge[room] = 1 if room in path else 0
            for doorway in model.building.doorways:
                self.knowledge[doorway] = 0

        if self.agent.type == 'leader':
            for room in model.building.rooms:
                self.knowledge[room] = 1
            for doorway in model.building.doorways:
                self.knowledge[doorway] = 0

    def entry_path(self, path: List[Room]):
        adjacent_rooms = list(path[-1].get_adjacent_rooms().values())
        random.shuffle(adjacent_rooms)
        for room in adjacent_rooms:
            if room in path:
                continue
            if room.is_outside:
                return path+[room]
            subpath = self.entry_path(path+[room])
            if subpath is not None and subpath[-1].is_outside:
                return subpath
        return None

    def follow_most(self, current_room):
        agents = self.model.get_agents_in_room(current_room)
        choices = {}
        for agent in agents:
            if agent.path is not None and len(agent.path)>1:
                if agent.path[1][1] in choices.keys():
                    choices[agent.path[1][1]] += 1
                else:
                    choices[agent.path[1][1]] =1
        max = 0
        choice = None
        for room in choices.keys():
            if choices[room] > max:
                max = choices[room]
                choice = room

        if choice is None:
            return None
        return [(0, current_room), (0, choice)]


    def get_path(self, current_room):
        """
        :param current_room: :return:
        TODO: funkcja ma sie wywolac za kazdym razem jak agent wchodzi no nowego pokoju (z nowym pokojem w argumencie). Tutaj ma byc logika racjonalnosci wyboru
        follower:
        top: zapytac lidera
        middle albo top ale nie ma lidera w pokoju: przeszulac wlasny graf
        worst: tam gdzie wiekszosc

        lider:
        top: przeszukac graf
        worst: za wszystkimi

        Opcjonalnie:
        zwisualizowac graficznie komunikacje miedzy agentami
        """
        path = None
        if self.agent.type == 'follower':
            r = 2**(1/self.rationality-1)-1
            x = 1/(1+r+r**2)
            rand = 0.1+random.random()*0.8
            # rand = 0.5
            if rand<x:
                path = self.ask_leader(current_room)
                # print('asking')
            if rand>x+r*x:
                path = self.follow_most(current_room)
                # print('following')
            if x < rand < x + r * x or path is None:
                # print('using knowledge')
                path = self.get_path_A(current_room)

        if self.agent.type == 'leader':
            rand = random.random()
            if rand>self.rationality:
                path = self.follow_most(current_room)
                # print('leader following')
            if rand<self.rationality or path is None:
                path = self.get_path_A(current_room)
                # print('leader rational')
        return path

    def ask_leader(self, current_room):
        agents = self.model.agents
        ask_distance = 200
        leaders = [agent for agent in agents if agent.type == 'leader' and distance(agent.body.get_position(), self.agent.body.get_position())<ask_distance]
        random.shuffle(leaders)
        if len(leaders):
            leader = leaders[0]
            return leader.decision_engine.get_path(current_room)
        else:
            return None
        # WYMIANA INFORMACJI O ZAGROZENIU

    def update(self, current_room):
        self.wkurfactor = 0
        adjacent_rooms = current_room.get_adjacent_rooms()
        self.knowledge[current_room] = 1
        for room in adjacent_rooms.values():
            if room.is_dangerous:
                self.knowledge[room] = 2

    def get_path_A(self, current_room: Room):
        UNKNOWN_COST = 1000
        def get_cost(src: Room, room: Room):#doorway: Doorway, room: Room):
            doorway = src.get_doorway(room)
            additional_cost = 0
            if self.knowledge[doorway]==3:
                additional_cost = 10000
            if self.agent.type == 'leader':
                CPA = 0.2
                # CPA*=10
                if src == current_room:
                    agents = self.model.get_agents_in_room(src)
                    for agent in agents:
                        if agent.path is not None and len(agent.path)>1 and agent.path[1][1]==room:
                            additional_cost += CPA
            #additional_cost = 0
            if room.is_outside:
                return 0+additional_cost
            elif self.knowledge[room] == 1:
                return doorway.distance+additional_cost
            elif self.knowledge[room] == 0:
                return UNKNOWN_COST+additional_cost
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
                # print('no exit')
                return
            adjacent_rooms = s[1].get_adjacent_rooms()
            for doorway, room in adjacent_rooms.items():
                if room not in opened.keys():
                    cost = get_cost(s[1],room)#doorway, room)
                    if cost is not None:
                        heappush(considered, (s[0]+cost, room))
            if s[1] not in opened.keys():
                opened[s[1]] = s[0]
            # print(s[1], s[0])

        path = [s]
        while path[0][1] != current_room:
            adjacent_rooms = path[0][1].get_adjacent_rooms()
            for doorway, room in adjacent_rooms.items():
                cost = get_cost(room, path[0][1])#doorway, room)
                if cost is not None:
                    if room in opened.keys() and room not in [element[1] for element in path]\
                            and abs(opened[room] - (path[0][0] - cost))< 0.001:
                        path.insert(0, (opened[room], room))
                        break
        return path

    def shout(self):
        has_danger_info = False
        for value in self.knowledge.values():
            if value == 2:
                has_danger_info = True
        if not has_danger_info:
            return
        shout_range = 2
        # print('shouting')
        self.agent.shouted = 10
        for agent in self.model.agents:
            if distance(self.agent.body.get_position(), agent.body.get_position())<shout_range:
                # print('\t informed')
                for key, value in self.knowledge.items():
                    if value==2:
                        if agent.decision_engine.knowledge[key] != value:
                            agent.path = None
                        agent.decision_engine.knowledge[key] = value



if __name__ == '__main__':
    pass
    # d1 = Doorway((0,0))
    # d2 = Doorway((10,0))
    # d3 = Doorway((20,0))
    # d4 = Doorway((30,0))
    # r1 = Room(doorways=[d1, d3], walls=[], name='1')
    # r2 = Room(doorways=[d1, d2], walls=[], name='2')
    # r3 = Room(doorways=[d2], walls=[], name='3')
    # r4 = Room(doorways=[d3, d4], walls=[], name='4')
    # r4.is_dangerous = True
    # building = Building(rooms=[r1,r2,r3,r4], doorways=[d1,d2,d3,d4])
    # model =
    # de = DecisionEngine(model=None, agent=Agent(''))
    # # de.knowledge[r4] = 2
    # path = de.get_path(r1)
    # print([element[1].name for element in path])


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
