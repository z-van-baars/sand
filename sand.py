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

    def set_occupied(self):
        self.is_occupied = True

    def set_vacant(self):
        self.is_occupied = False


class Entity(object):
    def __init__(self, pos_x, pos_y, width, height, color):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([width, height])
        self.sprite.image.fill(color)
        self.rect = self.sprite.image.get_rect()

    def tile_checkout(self, tile):
        tile.set_vacant()

    def tile_checkin(self, tile):
        tile.set_occupied()

    def fall(self, tiles, screen_width, screen_height):
        if self.pos_y < screen_height - 1:
            if not tiles[(self.pos_x, self.pos_y + 1)].is_occupied:
                self.tile_checkout(tiles[(self.pos_x, self.pos_y)])
                self.pos_y += 1
                self.tile_checkin(tiles[(self.pos_x, self.pos_y)])
                return True
            else:
                valid_second_choices = []
                if self.pos_x - 1 > 0 and not tiles[(self.pos_x - 1, self.pos_y + 1)].is_occupied:
                    valid_second_choices.append(tiles[(self.pos_x - 1, self.pos_y + 1)])
                if self.pos_y + 1 < screen_width - 1 and not tiles[(self.pos_x + 1, self.pos_y + 1)].is_occupied:
                    valid_second_choices.append(tiles[(self.pos_x + 1, self.pos_y + 1)])
                
                if len(valid_second_choices) > 0:
                    random_choice = random.choice(valid_second_choices)
                    self.tile_checkout(tiles[(self.pos_x, self.pos_y)])
                    self.pos_x = random_choice.x
                    self.pos_y = random_choice.y
                    self.tile_checkin(tiles[(self.pos_x, self.pos_y)])
                    return True
                else:
                    return False


class SandGrain(Entity):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 1, 1, colors.gold)


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


def spawn_entity(tiles, entities, spawn_settings):
    radius_tiles = get_brush(spawn_settings["Mouse Position"], spawn_settings["Brush Size"])
    valid_tiles = []
    for each in radius_tiles:
        if each in tiles:
            valid_tiles.append(each)
    random_tile = random.choice(valid_tiles)
    new_entity = spawn_settings["Entity Type"](random_tile[0], random_tile[1])
    entities.append(new_entity)


def get_brush_size_stamp(brush_size):
    font_arimo = pygame.font.SysFont('Arimo', 14, True, False)
    brush_size = str(brush_size)
    brush_size_stamp = font_arimo.render("Brush Size: {0}".format(brush_size), True, (colors.white))
    return brush_size_stamp

tiles = {}
for x in range(0, screen_width):
    for y in range(0, screen_height):
        tiles[(x, y)] = Tile(x, y)


entities = []
clock = pygame.time.Clock()

spawn_settings = {"Spawning": False,
                  "Mouse Position": (0, 0),
                  "Entity Type": SandGrain,
                  "Brush Size": 10}
brush_size_stamp = get_brush_size_stamp(spawn_settings["Brush Size"])

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

    if spawn_settings["Spawning"]:
        spawn_entity(tiles, entities, spawn_settings)
    for each in entities:
        each.fall(tiles, screen_width, screen_height)


    screen.blit(background, [0, 0])
    for each in entities:
        screen.blit(each.sprite.image, [each.pos_x, each.pos_y])
    pygame.draw.circle(screen,
                       colors.green_2,
                       spawn_settings["Mouse Position"],
                       spawn_settings["Brush Size"],
                       1)

    screen.blit(brush_size_stamp, [3, 2])

    pygame.display.flip()
    clock.tick(60)
