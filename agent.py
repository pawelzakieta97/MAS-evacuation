import random

from agent_body import AgentBody
import decision
from building import *

class Agent:
    def __init__(self, world, building, type='leader', x=None, y=None, spawn_room:Room=None):
        self.type = type
        self.current_room = None
        if spawn_room is not None:
            min_x = 99999999
            max_x = -99999999
            min_y = 99999999
            max_y = -99999999
            for wall in spawn_room.walls:
                min_x = min(min_x, wall.body.position[0])
                max_x = max(max_x, wall.body.position[0])
                min_y = min(min_y, wall.body.position[1])
                max_y = max(max_y, wall.body.position[1])
            x = random.randint(min_x+1, max_x-1)
            y = random.randint(min_y+1, max_y-1)
            self.current_room = spawn_room
        self.body = AgentBody(world, x=x, y=y, color=(255,255,0) if type == 'follower' else (255,0,255))
        self.decision_engine = decision.DecisionEngine(world, building, agent_type=type)
        self.path = None

    def update_path(self):
        self.path = self.decision_engine.get_path(self.current_room)

    def go_to_exit(self):
        if self.current_room.is_outside:
            return
        if self.path is None:
            self.update_path()
        # 1st room in the path list (index 0) is the current room
        dst_room = self.path[1][1]
        dst_doorway = self.current_room.get_doorway(dst_room)
        self.body.force_to_exit(dst_doorway)
        diff_x = self.body.get_position()[0] - dst_doorway.position[0]
        diff_y = self.body.get_position()[1] - dst_doorway.position[1]
        distance = math.sqrt(diff_x ** 2 + diff_y ** 2)
        if distance<0.5:
            for room in dst_doorway.rooms:
                if room != self.current_room:
                    self.current_room = room
                    self.path = None
                    break

    def draw(self, screen, render_settings):
        self.body.draw(screen, render_settings)