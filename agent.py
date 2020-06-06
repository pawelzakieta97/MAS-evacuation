import random

from agent_body import AgentBody
import decision
from building import *

class Agent:
    def __init__(self, model, type='leader', x=None, y=None, spawn_room:Room=None, rationality=None):
        self.type = type
        self.model = model
        self.current_room = None
        self.avg_vel = [0,0]
        self.shouted = 0
        self.informed = 0
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
        self.body = AgentBody(model.world, x=x, y=y, color=(255, 255, 0) if type == 'follower' else (255, 0, 255))
        self.decision_engine = decision.DecisionEngine(model, agent=self, rationality=rationality)
        self.path = None

    def go_to_exit(self):
        velocity = self.body.get_velocity()
        self.avg_vel[0] = self.avg_vel[0]*0.9+0.1*velocity[0]
        self.avg_vel[1] = self.avg_vel[1] * 0.9 + 0.1 * velocity[1]
        wkurfactor_threshold = 0.9
        if not self.current_room.is_outside:
            if self.avg_vel[0] ** 2 + self.avg_vel[1] ** 2 < 0.4:
                self.decision_engine.wkurfactor = (1.2+299*self.decision_engine.wkurfactor)/300
            else:
                self.decision_engine.wkurfactor = (299 * self.decision_engine.wkurfactor) / 300
            if self.decision_engine.wkurfactor>wkurfactor_threshold:
                self.decision_engine.knowledge[self.current_room.get_doorway(self.path[1][1])] = 3
                self.path = None
            if random.random()<self.decision_engine.wkurfactor*0.03:
                self.decision_engine.shout()

        update_room_prob = 0.05
        if random.random() < update_room_prob:
            updated_room = self.model.building.which_room(self.body.get_position())
            if updated_room != self.current_room:
                self.path = None
                if updated_room is not None:
                    self.current_room = updated_room
        if self.current_room.is_outside:
            self.body.maintain_force()
            return
        if self.path is None:
            self.decision_engine.update(self.current_room)
            self.path = self.decision_engine.get_path(self.current_room)
        # 1st room in the path list (index 0) is the current room
        if self.path is None or len(self.path) < 2:
            self.path = None
            return
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
        wkur_multiplier = (1.5-self.decision_engine.wkurfactor)/2
        self.body.color = [self.body.base_color[0]*wkur_multiplier,
                           self.body.base_color[1]*wkur_multiplier,
                           self.body.base_color[2]*wkur_multiplier]
        if self.shouted > 0:
            self.body.color = [25*self.shouted, 25*self.shouted, 25*self.shouted]
            self.shouted -=1
        self.body.draw(screen, render_settings)