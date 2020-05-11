import math

import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

import Box2D  # The main library
# Box2D.b2 maps Box2D.b2Vec2 to vec2 (and so on)
from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
from Box2D import (b2FixtureDef, b2PolygonShape,
                   b2Transform, b2Mul,
                   b2_pi)

class AgentBody:
    def __init__(self, world, x=10, y=15, color=None):
        if color is None:
            color = (255, 255, 0, 255)
        self.body = world.CreateDynamicBody(position=(x, y), linearDamping=1)
        self.fixture = self.body.CreateCircleFixture(radius=0.25, density=1, friction=0.3)
        self.circle = self.fixture.shape
        self.color = color

    def apply_force(self, force, point, wake=True):
        self.body.ApplyForce(force=force, point=point, wake=wake)

    def move_to_exit(self, exit, strength=1):
        exit_pos = exit.position
        position = self.get_position()
        diff_x = exit_pos[0] - position[0]
        diff_y = exit_pos[1] - position[1]
        distance = math.sqrt(diff_x**2+diff_y**2)
        force = (diff_x/distance*strength, diff_y/distance*strength)
        self.apply_force(force, position)

    def get_position(self):
        return self.body.position

    def draw(self, screen, render_settings):
        PPM = render_settings['PPM']
        SCREEN_HEIGHT = render_settings['SCREEN_HEIGHT']
        position = self.body.transform * self.circle.pos * PPM
        position = (position[0], SCREEN_HEIGHT - position[1])
        pygame.draw.circle(screen, self.color, [int(x) for x in position], int(self.circle.radius * PPM))

if __name__ == '__main__':
    PPM = 20.0  # pixels per meter
    TARGET_FPS = 60
    TIME_STEP = 1.0 / TARGET_FPS
    SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

    # --- pygame setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption('Simple pygame example')
    clock = pygame.time.Clock()

    # --- pybox2d world setup ---
    # Create the world
    world = world(gravity=(0, -10), doSleep=True)

    # And a static body to hold the ground shape
    ground_body = world.CreateStaticBody(
        position=(0, 0),
        shapes=polygonShape(box=(50, 1)),
    )
    agent = AgentBody(world)
    agents = [agent]
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
        # for body in world.bodies:
        #     # f = body.GetWorldVector(force=(0.0, 10))
        #     p = body.GetWorldPoint(localPoint=(0.0, 0))
        #     body.ApplyForce(force=(0, 40), point=p, wake=True)
        #     for fixture in body.fixtures:
        #         fixture.shape.draw(body, fixture)
        for agent in agents:
            agent.draw(screen)

        # Make Box2D simulate the physics of our world for one step.
        world.Step(TIME_STEP, 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    print('Done!')