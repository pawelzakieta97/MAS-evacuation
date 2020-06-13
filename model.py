from agent_body import AgentBody
from building import *
import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)
import numpy as np

from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
import random
import agent


class Model:
    def __init__(self, num_agents=30, wrld=None, building=None, spawn=None, rationality=None, leader_proportion=0.05, door_width=None):
        self.render_settings = {'PPM': 20, 'SCREEN_HEIGHT': 480, 'SCREEN_WIDTH': 640,
                           'TARGET_FPS': 60, 'TIME_STEP': 1 / 60}
        self.screen = pygame.display.set_mode(
            (self.render_settings['SCREEN_WIDTH'], self.render_settings['SCREEN_HEIGHT']), 0,
            32)
        pygame.display.set_caption('Simple pygame example')
        self.clock = pygame.time.Clock()


        # --- pybox2d world setup ---
        # Create the world
        if door_width is None:
            door_width = 1.5
        if wrld is None and building is None:
            self.world = world(gravity=(0, 0), doSleep=True)
            doorways = [Doorway((10, 8), door_width),
                        Doorway((10, 12), door_width),
                        Doorway((20, 5), door_width),
                        Doorway((20, 15), door_width),
                        Doorway((30, 5), door_width),
                        Doorway((15, 10), door_width),
                        Doorway((25, 10), door_width),
                        Doorway((30, 15), door_width)]
            room1 = create_room(self.world, 15, 0, 5, 10,
                                east_doorways=[doorways[0], doorways[1]], name='r 1')
            room2 = create_room(self.world, 20, 10, 10, 20, west_doorways=[doorways[1]], #south_doorways=[doorways[5]],
                                east_doorways=[doorways[3]], name='r 2')
            room3 = create_room(self.world, 10, 10, 0, 20, west_doorways=[doorways[0]], #north_doorways=[doorways[5]],
                                east_doorways=[doorways[2]], name='r 3')
            room4 = create_room(self.world, 20, 20, 10, 30, west_doorways=[doorways[3]], south_doorways=[doorways[6]], east_doorways=[doorways[7]],
                                name='r 4')
            room5 = create_room(self.world, 10, 20, 0, 30, west_doorways=[doorways[2]], north_doorways=[doorways[6]],
                                east_doorways=[doorways[4]], name='r 5')
            # room1.is_dangerous = True
            self.building = Building(rooms=[room1, room2, room3, room4, room5],
                                     doorways=doorways)
            spawn = room1

        self.agents = [agent.Agent(self, type='follower', spawn_room=random.choice([room1, room2]), rationality=rationality) for i in range(int((1-leader_proportion)*num_agents))]
        leaders = [agent.Agent(self, type='leader', spawn_room=random.choice([room1, room2]), rationality=rationality) for i in range(int(leader_proportion*num_agents))]
        # self.agents = [agent.Agent(self, type='follower', spawn_room=spawn, rationality=rationality) for i in range(int((1-leader_proportion)*num_agents))]
        # leaders = [agent.Agent(self, type='leader', spawn_room=spawn, rationality=rationality) for i in range(int(leader_proportion*num_agents))]
        
        self.agents += leaders
        self.num_agents = num_agents
        self.running = True

    def step(self, outside):
        for event in pygame.event.get():
            if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE):
                # The user closed the window or pressed escape
                self.running = False
        self.screen.fill((0, 0, 0, 0))
        # Draw the world
        self.building.draw(self.screen, self.render_settings)
        for agent in self.agents:
            agent.draw(self.screen, self.render_settings)
            agent.go_to_exit()
            if agent.current_room.is_outside:
                outside += 1

        # Make Box2D simulate the physics of our world for one step.
        self.world.Step(self.render_settings['TIME_STEP'], 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        return outside

    def run(self):
        steps = 0
        agents_outside = np.full((5000, 1), len(self.agents))
        while self.running:
            outside = self.step(0)
            agents_outside[steps] = outside
            steps += 1
            if outside == len(self.agents) or steps == 4999:
                return agents_outside
            self.clock.tick(self.render_settings['TARGET_FPS'])

    def get_agents_in_room(self, room):
        agents = []
        for agent in self.agents:
            if agent.current_room == room:
                agents.append(agent)
        return agents


if __name__ == '__main__':
    model = Model(50, rationality=0.01, leader_proportion=0.05)
    model.run()
    
    # door_widths = [1, 1.25, 1.5, 1.75, 2]
    # rationalities = [0.01, None, 1]
    # leader_proportions = [0.025, 0.05, 0.1, 0.5]

    # for rationality in rationalities:
    #     for leader_proportion in leader_proportions:
    #         for door_width in door_widths: 
    #             for i in range(10):                    
    #                 model = Model(50, rationality=rationality, leader_proportion=leader_proportion, door_width=door_width)
    #                 np.savetxt('results/i_' + str(i) + '_R_' + str(rationality) + '_DW_' + str(door_width) + '_LP_' + str(leader_proportion) + '.csv', model.run(), delimiter=' ')
    
    
