from agent_body import AgentBody
from building import *
import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
import random

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
    # wall = Wall(world, (0,0), (31, 20))
    room = create_room(world, 20,10,0,30, [], [], [], east_exits=[Exit((30,10), 1), Exit((30,15), 1)])
    num_agents = 30
    agents = [AgentBody(world, x,y) for x,y in [(random.randint(1, 19), random.randint(1, 19)) for i in range(num_agents)]]
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
        room.draw(screen, render_settings)
        for agent in agents:
            agent.draw(screen, render_settings)
            agent.move_to_exit(room.exits[0])

        # Make Box2D simulate the physics of our world for one step.
        world.Step(render_settings['TIME_STEP'], 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        clock.tick(render_settings['TARGET_FPS'])

    pygame.quit()
    print('Done!')