import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

import Box2D  # The main library
# Box2D.b2 maps Box2D.b2Vec2 to vec2 (and so on)
from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
from Box2D import (b2FixtureDef, b2PolygonShape,
                   b2Transform, b2Mul,
                   b2_pi)
import math

class Wall:
    def __init__(self, world, start_point, end_point, width=0.5, color=(100,100,100,255)):
        self.color = color
        length = math.sqrt((end_point[0]-start_point[0])**2+(end_point[1]-start_point[1])**2)
        angle = math.atan2(end_point[1]-start_point[1], end_point[0]-start_point[0])
        self.body = world.CreateStaticBody(position=((start_point[0]+end_point[0])/2, (start_point[1]+end_point[1])/2), angle=angle)
        # self.body = world.CreateDynamicBody(position=((start_point[0]+end_point[0])/2, (start_point[1]+end_point[1])/2), angle=angle)
        self.fixture = self.body.CreatePolygonFixture(box=(length/2, width/2), density=1, friction=0.3)
        self.box = self.fixture.shape

    def draw(self, screen, render_settings):
        PPM = render_settings['PPM']
        SCREEN_HEIGHT = render_settings['SCREEN_HEIGHT']
        vertices = [(self.body.transform * v) * PPM for v in self.box.vertices]
        vertices = [(v[0], SCREEN_HEIGHT - v[1]) for v in vertices]
        pygame.draw.polygon(screen, self.color, vertices)

class Exit:
    def __init__(self, position, width=1, terminal=False):
        self.position = position
        self.width = width
        self.is_terminal = terminal
        self.rooms = ()
        self.distance = 0

    def set_rooms(self, room1, room2):
        """Set rooms that are connected by this exit

        :param (Room) room1:
        :param (Room) room2:
        """
        self.rooms = (room1, room2)
        diff_x1 = room1.com[0]-self.position[0]
        diff_y1 = room1.com[1] - self.position[1]
        diff_x2 = room2.com[0] - self.position[0]
        diff_y2 = room2.com[1] - self.position[1]
        self.distance = math.sqrt(diff_x1**2+diff_y1**2)+math.sqrt(diff_x2**2+diff_y2**2)

class Room:
    def __init__(self, walls, exits):
        self.walls = walls
        self.exits = exits
        min_x = 99999999
        max_x = -99999999
        min_y = 99999999
        max_y = -99999999

        for wall in walls:
            min_x = min(min_x, wall.body.position[0])
            max_x = max(max_x, wall.body.position[0])
            min_y = min(min_y, wall.body.position[1])
            max_y = max(max_y, wall.body.position[1])
        self.com = ((min_x+max_x)/2, (min_y+max_y)/2)

    def draw(self, screen, render_settings):
        for wall in self.walls:
            wall.draw(screen, render_settings)

    def get_adjacent_rooms(self):
        adjacent_rooms = []
        for exit in self.exits:
            for room in exit.rooms:
                if room is not self:
                    adjacent_rooms.append(room)

def create_room(world,  north_wall, west_wall, south_wall, east_wall, north_exits=None, west_exits=None, south_exits=None, east_exits=None):
    if north_exits is None and west_exits is None and south_exits is None and east_exits is None:
        raise ValueError('room must have at least one exit')
    north_exits = sorted(north_exits, key=lambda exit: exit.position[0])
    west_exits = sorted(west_exits, key=lambda exit: exit.position[1])
    south_exits = sorted(south_exits, key=lambda exit: exit.position[0])
    east_exits = sorted(east_exits, key=lambda exit: exit.position[1])

    ne_corner = (east_wall, north_wall)
    nw_corner = (west_wall, north_wall)
    sw_corner = (west_wall, south_wall)
    se_corner = (east_wall, south_wall)

    walls = []
    last_point = nw_corner
    for north_exit in north_exits:
        exit_border_west = (north_exit.position[0]-north_exit.width/2, north_exit.position[1])
        walls.append(Wall(world, last_point, exit_border_west))
        last_point = (north_exit.position[0]+north_exit.width/2, north_exit.position[1])
    walls.append(Wall(world, last_point, ne_corner))

    last_point = sw_corner
    for west_exit in west_exits:
        exit_border_south = (west_exit.position[0], west_exit.position[1]-west_exit.width/2)
        walls.append(Wall(world, last_point, exit_border_south))
        last_point = (west_exit.position[0], west_exit.position[1]+west_exit.width/2)
    walls.append(Wall(world, last_point, nw_corner))

    last_point = sw_corner
    for south_exit in south_exits:
        exit_border_west = (
        south_exit.position[0] - south_exit.width / 2, south_exit.position[1])
        walls.append(Wall(world, last_point, exit_border_west))
        last_point = (south_exit.position[0] + south_exit.width / 2, south_exit.position[1])
    walls.append(Wall(world, last_point, se_corner))

    last_point = se_corner
    for east_exit in east_exits:
        exit_border_south = (
        east_exit.position[0], east_exit.position[1] - east_exit.width / 2)
        walls.append(Wall(world, last_point, exit_border_south))
        last_point = (east_exit.position[0], east_exit.position[1] + east_exit.width / 2)
    walls.append(Wall(world, last_point, ne_corner))
    return Room(walls=walls, exits=north_exits+west_exits+south_exits+east_exits)

class Building:
    def __init__(self, rooms, exits):
        self.rooms = rooms
        for exit in exits:
            rooms = []
            for room in rooms:
                if exit in room.exits:
                    rooms.append(room)
            if len(rooms) == 2:
                exit.set_rooms(rooms[0], rooms[1])
            if len(rooms) == 1:
                exit.is_terminal = True
        self.exits = exits




if __name__ == '__main__':
    render_settings = {'PPM': 20, 'SCREEN_HEIGHT': 480, 'SCREEN_WIDTH': 640, 'TARGET_FPS':60, 'TIME_STEP': 1/60}
    screen = pygame.display.set_mode((render_settings['SCREEN_WIDTH'], render_settings['SCREEN_HEIGHT']), 0, 32)
    pygame.display.set_caption('Simple pygame example')
    clock = pygame.time.Clock()

    # --- pybox2d world setup ---
    # Create the world
    world = world(gravity=(0, -10), doSleep=True)
    # wall = Wall(world, (0,0), (31, 20))
    # room = Room1out(world, (10,10), 20,20)
    room = create_room(world, 20,10,0,30, [], [], [], east_exits=[Exit((30,10), 4), Exit((30,15), 1)])
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

        # Make Box2D simulate the physics of our world for one step.
        world.Step(render_settings['TIME_STEP'], 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        clock.tick(render_settings['TARGET_FPS'])

    pygame.quit()
    print('Done!')
