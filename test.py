from agent_body import AgentBody
from building import *
import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
import random
import agent

if __name__ == "__main__":
    render_settings = {'PPM': 20, 'SCREEN_HEIGHT': 480, 'SCREEN_WIDTH': 640,
                       'TARGET_FPS': 60, 'TIME_STEP': 1 / 60}
    screen = pygame.display.set_mode(
        (render_settings['SCREEN_WIDTH'], render_settings['SCREEN_HEIGHT']), 0,
        32)
    pygame.display.set_caption('Simple pygame example')
    clock = pygame.time.Clock()

    # --- pybox2d world setup ---
    # Create the world
    world = world(gravity=(0, 0), doSleep=True)
    doorways = [Doorway((10, 8), 1.25), Doorway((10, 12), 1.25), Doorway((20, 5), 1.25),
                Doorway((20, 15), 1.25), Doorway((30, 5), 1.25)]
    room1 = create_room(world, 15, 0, 5, 10,
                        east_doorways=[doorways[0], doorways[1]], name='r 1')
    room2 = create_room(world, 20, 10, 10, 20, west_doorways=[doorways[1]],
                        east_doorways=[doorways[3]], name='r 2')
    room3 = create_room(world, 10, 10, 0, 20, west_doorways=[doorways[0]],
                        east_doorways=[doorways[2]], name='r 3')
    room4 = create_room(world, 20, 20, 10, 30, west_doorways=[doorways[3]], name='r 4')
    room5 = create_room(world, 10, 20, 0, 30, west_doorways=[doorways[2]],
                        east_doorways=[doorways[4]], name='r 5')
    building = Building(rooms=[room1, room2, room3, room4, room5],
                        doorways=doorways)
    num_agents = 30
    # agents = [AgentBody(world, x,y) for x,y in [(random.randint(1, 19), random.randint(1, 19)) for i in range(num_agents)]]
    agents = [agent.Agent(world, building, type='leader', spawn_room=room4) for i in range(num_agents)]
    running = True
    while running:
        # Check the event queue
        for event in pygame.event.get():
            if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE):
                # The user closed the window or pressed escape
                running = False

        screen.fill((0, 0, 0, 0))
        # Draw the world
        building.draw(screen, render_settings)
        for agent in agents:
            agent.draw(screen, render_settings)
            agent.go_to_exit()

        # Make Box2D simulate the physics of our world for one step.
        world.Step(render_settings['TIME_STEP'], 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        clock.tick(render_settings['TARGET_FPS'])

    pygame.quit()
    print('Done!')