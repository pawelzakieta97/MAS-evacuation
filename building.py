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

class Doorway:
    def __init__(self, position, width=1, active=True):
        self.position = position
        self.width = width
        self.is_active = active
        self.rooms = ()
        self.distance = 0

    def set_rooms(self, room1, room2):
        """Set rooms that are connected by this exit

        :param (Room) room1:
        :param (Room) room2:
        """
        self.rooms = (room1, room2)
        diff_x1 = room1.position[0] - self.position[0]
        diff_y1 = room1.position[1] - self.position[1]
        diff_x2 = room2.position[0] - self.position[0]
        diff_y2 = room2.position[1] - self.position[1]
        diff_x_total = room1.position[0] - room2.position[0]
        diff_y_total = room1.position[1] - room2.position[1]
        self.distance = math.sqrt(diff_x1**2+diff_y1**2)+math.sqrt(diff_x2**2+diff_y2**2)
        self.distance = math.sqrt(diff_x_total**2+diff_y_total**2)

    def set_exit(self, room):
        self.rooms = (room, BuildingExit(self))


class Room:
    def __init__(self, walls, doorways, name='room'):
        self.name = name
        self.walls = walls
        self.doorways = doorways
        self.is_outside = False
        self.is_dangerous = False
        min_x = 99999999
        max_x = -99999999
        min_y = 99999999
        max_y = -99999999

        for doorway in doorways:
            min_x = min(min_x, doorway.position[0])
            max_x = max(max_x, doorway.position[0])
            min_y = min(min_y, doorway.position[1])
            max_y = max(max_y, doorway.position[1])
        self.position = ((min_x + max_x) / 2, (min_y + max_y) / 2)

    def draw(self, screen, render_settings):
        for wall in self.walls:
            wall.draw(screen, render_settings)

    def get_adjacent_rooms(self):
        adjacent_rooms = {}
        for doorway in self.doorways:
            for room in doorway.rooms:
                if room is not self:
                    adjacent_rooms[doorway] = room
        return adjacent_rooms

    def get_doorway(self, room):
        for doorway in self.doorways:
            if room in doorway.rooms:
                return doorway

    def set_dangerous(self):
        self.is_dangerous = True

    def __lt__(self, room):
        return False

    def __str__(self):
        return self.name

class BuildingExit(Room):
    def __init__(self, exit):
        super().__init__(walls=[], doorways=[exit], name='exit')
        self.com = exit.position
        self.is_outside = True

def create_room(world,  north_wall, west_wall, south_wall, east_wall, north_doorways=None, west_doorways=None, south_doorways=None, east_doorways=None, name=None):
    if north_doorways is None and west_doorways is None and south_doorways is None and east_doorways is None:
        raise ValueError('room must have at least one doorway')
    if north_doorways is None:
        north_doorways = []
    if west_doorways is None:
        west_doorways = []
    if south_doorways is None:
        south_doorways = []
    if east_doorways is None:
        east_doorways = []
    north_doorways = sorted(north_doorways, key=lambda doorway: doorway.position[0])
    west_doorways = sorted(west_doorways, key=lambda doorway: doorway.position[1])
    south_doorways = sorted(south_doorways, key=lambda doorway: doorway.position[0])
    east_doorways = sorted(east_doorways, key=lambda doorway: doorway.position[1])

    ne_corner = (east_wall, north_wall)
    nw_corner = (west_wall, north_wall)
    sw_corner = (west_wall, south_wall)
    se_corner = (east_wall, south_wall)

    walls = []
    last_point = nw_corner
    for north_doorway in north_doorways:
        doorway_border_west = (north_doorway.position[0]-north_doorway.width/2, north_doorway.position[1])
        walls.append(Wall(world, last_point, doorway_border_west))
        last_point = (north_doorway.position[0]+north_doorway.width/2, north_doorway.position[1])
    walls.append(Wall(world, last_point, ne_corner))

    last_point = sw_corner
    for west_doorway in west_doorways:
        doorway_border_south = (west_doorway.position[0], west_doorway.position[1]-west_doorway.width/2)
        walls.append(Wall(world, last_point, doorway_border_south))
        last_point = (west_doorway.position[0], west_doorway.position[1]+west_doorway.width/2)
    walls.append(Wall(world, last_point, nw_corner))

    last_point = sw_corner
    for south_doorway in south_doorways:
        doorway_border_west = (
        south_doorway.position[0] - south_doorway.width / 2, south_doorway.position[1])
        walls.append(Wall(world, last_point, doorway_border_west))
        last_point = (south_doorway.position[0] + south_doorway.width / 2, south_doorway.position[1])
    walls.append(Wall(world, last_point, se_corner))

    last_point = se_corner
    for east_doorway in east_doorways:
        doorway_border_south = (
        east_doorway.position[0], east_doorway.position[1] - east_doorway.width / 2)
        walls.append(Wall(world, last_point, doorway_border_south))
        last_point = (east_doorway.position[0], east_doorway.position[1] + east_doorway.width / 2)
    walls.append(Wall(world, last_point, ne_corner))
    return Room(walls=walls, doorways=north_doorways + west_doorways + south_doorways + east_doorways, name=name)


class Building:
    def __init__(self, rooms, doorways):
        self.rooms = rooms
        for doorway in doorways:
            rooms_connected = []
            for room in rooms:
                if doorway in room.doorways:
                    rooms_connected.append(room)
            if len(rooms_connected) == 2:
                doorway.set_rooms(rooms_connected[0], rooms_connected[1])
            if len(rooms_connected) == 1:
                doorway.set_exit(rooms_connected[0])
        self.doorways = doorways

    def draw(self, screen, render_settings):
        for room in self.rooms:
            room.draw(screen, render_settings)

    def which_room(self, position):
        for room in self.rooms:
            if room.is_outside:
                continue
            wall_x_coords = [wall.body.position[0] for wall in room.walls]
            wall_y_coords = [wall.body.position[1] for wall in room.walls]
            if position[0] > min(wall_x_coords) and position[0] < max(wall_x_coords) and position[1] > min(wall_y_coords) and position[1] < max(wall_y_coords):
                return room
        return BuildingExit(self.doorways[0])


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
    doorways = [Doorway((10, 8)), Doorway((10, 12)), Doorway((20, 5)), Doorway((20, 15)), Doorway((30, 5))]
    room1 = create_room(world, 15, 0, 5, 10, east_doorways=[doorways[0], doorways[1]])
    room2 = create_room(world, 20, 10, 10, 20, west_doorways=[doorways[1]], east_doorways=[doorways[3]])
    room3 = create_room(world, 10, 10, 0, 20, west_doorways=[doorways[0]], east_doorways=[doorways[2]])
    room4 = create_room(world, 20, 20, 10, 30, west_doorways=[doorways[3]])
    room5 = create_room(world, 10, 20, 0, 30, west_doorways=[doorways[2]], east_doorways=[doorways[4]])
    # room = create_room(world, 20,10,0,30, [], [], [], east_exits=[Exit((30,10), 4), Exit((30,15), 1)])
    building = Building(rooms=[room1, room2, room3, room4, room5], doorways=doorways)
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

        # Make Box2D simulate the physics of our world for one step.
        world.Step(render_settings['TIME_STEP'], 10, 10)

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        clock.tick(render_settings['TARGET_FPS'])

    pygame.quit()
    print('Done!')
