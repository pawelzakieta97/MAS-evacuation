from agent_body import AgentBody
from building import *
import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
import random
import agent


class Model:
    def __init__(self, num_agents=30, wrld = None, building=None, spawn=None):
        self.render_settings = {'PPM': 20, 'SCREEN_HEIGHT': 480, 'SCREEN_WIDTH': 640,
                           'TARGET_FPS': 60, 'TIME_STEP': 1 / 60}
        self.screen = pygame.display.set_mode(
            (self.render_settings['SCREEN_WIDTH'], self.render_settings['SCREEN_HEIGHT']), 0,
            32)
        pygame.display.set_caption('Simple pygame example')
        self.clock = pygame.time.Clock()

        # --- pybox2d world setup ---
        # Create the world
        if wrld is None and building is None:
            self.world = world(gravity=(0, 0), doSleep=True)
            doorways = [Doorway((10, 8), 1.5), Doorway((10, 12), 1.5), Doorway((20, 5), 1.5),
                        Doorway((20, 15), 1.5), Doorway((30, 5), 1.5), Doorway((15, 10), 1.5), Doorway((25, 10), 1.5),]
            room1 = create_room(self.world, 15, 0, 5, 10,
                                east_doorways=[doorways[0], doorways[1]], name='r 1')
            room2 = create_room(self.world, 20, 10, 10, 20, west_doorways=[doorways[1]], #south_doorways=[doorways[5]],
                                east_doorways=[doorways[3]], name='r 2')
            room3 = create_room(self.world, 10, 10, 0, 20, west_doorways=[doorways[0]], #north_doorways=[doorways[5]],
                                east_doorways=[doorways[2]], name='r 3')
            room4 = create_room(self.world, 20, 20, 10, 30, west_doorways=[doorways[3]], south_doorways=[doorways[6]],
                                name='r 4')
            room5 = create_room(self.world, 10, 20, 0, 30, west_doorways=[doorways[2]], north_doorways=[doorways[6]],
                                east_doorways=[doorways[4]], name='r 5')
            self.building = Building(rooms=[room1, room2, room3, room4, room5],
                                doorways=doorways)
            spawn = room2

        self.agents = [agent.Agent(self, type='follower', spawn_room=spawn) for i in range(num_agents)]

        self.running = True

    def step(self):
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

        # Make Box2D simulate the physics of our world for one step.
        self.world.Step(self.render_settings['TIME_STEP'], 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()

    def run(self):
        while self.running:
            self.step()
            self.clock.tick(self.render_settings['TARGET_FPS'])

    def get_agents_in_room(self, room):
        agents = []
        for agent in self.agents:
            if agent.current_room == room:
                agents.append(agent)
        return agents


if __name__ == '__main__':
    model = Model(1)
    model.run()
