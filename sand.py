import pygame
import colors
import math
import random

screen_width = 600#int(input("Width?\n"))
screen_height = 600#int(input("Height?\n"))
pygame.init()
screen = pygame.display.set_mode([screen_width, screen_height])
background = pygame.Surface((screen_width, screen_height))
background.fill(colors.black)


class Tile(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_occupied = False
        self.entity = None

    def set_occupied(self, entity):
        self.is_occupied = True
        self.entity = entity

    def set_vacant(self):
        self.is_occupied = False
        self.entity = None


class Entity(object):
    dynamic = False
    name = "N/A"

    def __init__(self, pos_x, pos_y, width, height, color, inertia):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.inertia = inertia
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([width, height])
        self.sprite.image.fill(color)
        self.rect = self.sprite.image.get_rect()

    def tile_checkout(self, tile):
        tile.set_vacant()

    def tile_checkin(self, tile):
        tile.set_occupied(self)

    def fall(self, tiles, screen_width, screen_height):
        if self.pos_y < screen_height - 1:
            if not tiles[(self.pos_x, self.pos_y + 1)].is_occupied:
                self.tile_checkout(tiles[(self.pos_x, self.pos_y)])
                self.pos_y += 1
                self.tile_checkin(tiles[(self.pos_x, self.pos_y)])
            else:
                valid_second_choices = []
                if self.pos_x - 1 > 0 and not tiles[(self.pos_x - 1, self.pos_y + 1)].is_occupied:
                    valid_second_choices.append(tiles[(self.pos_x - 1, self.pos_y + 1)])
                if self.pos_x + 1 < screen_width - 1 and not tiles[(self.pos_x + 1, self.pos_y + 1)].is_occupied:
                    valid_second_choices.append(tiles[(self.pos_x + 1, self.pos_y + 1)])
                
                if len(valid_second_choices) > 0:
                    random_choice = random.choice(valid_second_choices)
                    self.tile_checkout(tiles[(self.pos_x, self.pos_y)])
                    self.pos_x = random_choice.x
                    self.pos_y = random_choice.y
                    self.tile_checkin(tiles[(self.pos_x, self.pos_y)])
                    


class SandGrain(Entity):
    dynamic = True
    spawn_behavior = 0
    name = "Sand"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 1, 1, colors.gold, 1)


class Water(Entity):
    dynamic = True
    spawn_behavior = 0
    name = "Water"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 1, 1, colors.bright_blue, 10000)


class Stone(Entity):
    dynamic = False
    spawn_behavior = 1
    name = "Stone"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 1, 1, colors.blue_grey, None)


def distance(a, b, x, y):
    a1 = abs(a - x)
    b1 = abs(b - y)
    c = math.sqrt((a1 * a1) + (b1 * b1))
    return c


def get_brush(pos, radius):
    tile_tuples = []
    for x in range(pos[0] - radius, pos[0] + radius):
        for y in range(pos[1] - radius, pos[1] + radius):
            if distance(pos[0], pos[1], x, y) < radius:
                tile_tuples.append((x, y))
    return tile_tuples


def mouse_down(event, spawn_settings):
    if event.button == 1:
        spawn_settings["Spawning"] = True
    elif event.button == 4:
        spawn_settings["Brush Size"] = min(30, spawn_settings["Brush Size"] + 1)
    elif event.button == 5:
        spawn_settings["Brush Size"] = max(1, spawn_settings["Brush Size"] - 1)


def mouse_up(event, spawn_settings):
    if event.button == 1:
        spawn_settings["Spawning"] = False


def key_down(event, spawn_settings):
    entity_types = [SandGrain,
                    Stone,
                    Water]
    type_index = entity_types.index(spawn_settings["Entity Type"])
    if event.key == pygame.K_UP:
        if type_index == 0:
            type_index = len(entity_types) - 1
        else:
            type_index -= 1
    elif event.key == pygame.K_DOWN:
        if type_index == len(entity_types) - 1:
            type_index = 0
        else:
            type_index += 1
    spawn_settings["Entity Type"] = entity_types[type_index]


def spawn_entity(tiles, static_entities, dynamic_entities, spawn_settings):
    radius_tiles = get_brush(spawn_settings["Mouse Position"], spawn_settings["Brush Size"])
    if spawn_settings["Entity Type"].spawn_behavior == 0:
        valid_tiles = []
        for each in radius_tiles:
            if each in tiles:
                valid_tiles.append(each)
        random_tile = random.choice(valid_tiles)
        new_entity = spawn_settings["Entity Type"](random_tile[0], random_tile[1])
        dynamic_entities.add(new_entity)


    elif spawn_settings["Entity Type"].spawn_behavior == 1:
        valid_tiles = []
        for each in radius_tiles:
            if each in tiles:
                valid_tiles.append(each)
        for each in valid_tiles:
            x = each[0]
            y = each[1]

            if tiles[x, y].is_occupied:
                if not tiles[x, y].entity.dynamic:
                    static_entities.remove(tiles[x, y].entity)
                if tiles[x, y].entity.dynamic:
                    dynamic_entities.remove(tiles[x, y].entity)
                tiles[x, y].entity.tile_checkout(tiles[x, y])

            new_entity = spawn_settings["Entity Type"](x, y)
            static_entities.add(new_entity)
            new_entity.tile_checkin(tiles[(x, y)])


def get_brush_size_stamp(brush_size):
    font_arimo = pygame.font.SysFont('Arimo', 14, True, False)
    brush_size = str(brush_size)
    brush_size_stamp = font_arimo.render("Brush Size: {0}".format(brush_size), True, (colors.white))
    return brush_size_stamp


def get_entity_count_stamp(static_entities, dynamic_entities, screen_width):
    font_arimo = pygame.font.SysFont('Arimo', 14, True, False)
    static_entities = str(len(static_entities))
    dynamic_entities = str(len(dynamic_entities))
    entity_count_stamp = font_arimo.render("S: {0}  D: {1}".format(static_entities, dynamic_entities), True, (colors.white))
    width = entity_count_stamp.get_width()
    spacer = screen_width - (width + 3)
    return entity_count_stamp, spacer

def get_entity_type_stamp(spawn_settings):
    font_arimo = pygame.font.SysFont('Arimo', 14, True, False)
    name = spawn_settings["Entity Type"].name
    entity_type_stamp = font_arimo.render("{0}".format(name), True, (colors.white))
    return entity_type_stamp


def update_static_layer(static_layer, static_entities):
    static_layer.fill(colors.key)
    for each in static_entities:
        static_layer.blit(each.sprite.image, [each.pos_x, each.pos_y])
    static_layer.set_colorkey(colors.key)
    static_layer = static_layer.convert_alpha()
    return static_layer

tiles = {}
for x in range(0, screen_width):
    for y in range(0, screen_height):
        tiles[(x, y)] = Tile(x, y)

static_entities = set()
dynamic_entities = set()
clock = pygame.time.Clock()

spawn_settings = {"Spawning": False,
                  "Mouse Position": (0, 0),
                  "Entity Type": SandGrain,
                  "Brush Size": 10}
entity_type_stamp = get_entity_type_stamp(spawn_settings)
brush_size_stamp = get_brush_size_stamp(spawn_settings["Brush Size"])
static_layer = pygame.Surface((screen_width, screen_height))
static_layer = update_static_layer(static_layer, static_entities)

while True:
    spawn_settings["Mouse Position"] = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down(event, spawn_settings)
            brush_size_stamp = get_brush_size_stamp(spawn_settings["Brush Size"])
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_up(event, spawn_settings)
            brush_size_stamp = get_brush_size_stamp(spawn_settings["Brush Size"])
        elif event.type == pygame.KEYDOWN:
            key_down(event, spawn_settings)
            entity_type_stamp = get_entity_type_stamp(spawn_settings)

    if spawn_settings["Spawning"]:
        spawn_entity(tiles, static_entities, dynamic_entities, spawn_settings)
        static_layer = update_static_layer(static_layer, static_entities)

    new_dynamic_entities = set()
    for each in dynamic_entities:
        each.fall(tiles, screen_width, screen_height)
        if each.inertia == 0:
            static_entities.add(each)
        else:
            new_dynamic_entities.add(each)
    dynamic_entities = new_dynamic_entities
    entity_count_stamp, spacer = get_entity_count_stamp(static_entities,
                                                        dynamic_entities,
                                                        screen_width)



    screen.blit(background, [0, 0])

    screen.blit(static_layer, [0, 0])
    for each in dynamic_entities:
        screen.blit(each.sprite.image, [each.pos_x, each.pos_y])
    pygame.draw.circle(screen,
                       colors.green_2,
                       spawn_settings["Mouse Position"],
                       spawn_settings["Brush Size"],
                       1)

    screen.blit(brush_size_stamp, [3, 2])
    screen.blit(entity_count_stamp, [spacer, 2])
    screen.blit(entity_type_stamp, [screen_width / 2 - (entity_type_stamp.get_width() / 2), 2])

    pygame.display.flip()
    clock.tick(60)
