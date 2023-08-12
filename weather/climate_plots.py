from typing import NewType, Union, List, Tuple
from json import load
import math
import cairo


class Color:
    def __init__(self, r, g, b, a=1):
        self.color = (r, g, b, a)

    def __iter__(self):
        return iter(self.color)


class Grid:

    def __init__(self, x_dim, y_dim, x_offset=0.05, y_offset=0.05):
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.x_offset = x_offset
        self.y_offset = y_offset

    def coords(self, x, y):
        return self.x_offset + x * self.x_dim, self.y_offset + y * self.y_dim


white = Color(1, 1, 1)


def weather_set(x, y, context, temps, rains, winds, top_label, left_label=None):
    y += 0.05
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(0.1)
    ctx.select_font_face("Arial",
                         cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)
    if left_label is not None:
        ctx.move_to(x+0.04, y+0.75)
        ctx.rotate(-90*math.pi/180)
        ctx.show_text(left_label)
        ctx.rotate(90*math.pi/180)
    x += 0.1
    ctx.move_to(x, y)
    ctx.show_text(top_label)
    y += 0.04

    temps = [6-t for t in temps]
    rains = [3-r for r in rains]
    winds = [3-w for w in winds]
    temperatures(x, y, context, temps)
    rain(x + 0.2, y, context, rains)
    wind(x + 0.4, y, context, winds)


def column_of_boxes(
                    x: float,
                    y: float,
                    n: int,
                    width: float,
                    height: float,
                    context: cairo.Context,
                    colors: Union[Color, List[Color]]):
    if type(colors) == Color:
        colors = [colors]*n
    for i in range(n):
        context.rectangle(x, y + i*height, width, height)
        context.set_source_rgba(*colors[i])
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.set_line_width(0.02)
        context.stroke()


def temperatures(x, y, context, enabled: Union[bool, List[int]]=True):
    colors = [
        Color(0.940, 0.0188, 0.203),
        Color(0.980, 0.304, 0.304),
        Color(0.890, 0.587, 0.587),
        Color(0.599, 0.727, 0.950),
        Color(0.360, 0.595, 1.00),
        Color(0.167, 0.447, 0.930),
        Color(0.0666, 0.0528, 0.880)
    ]
    if enabled is True:
        enabled = range(len(colors))
    for i in range(len(colors)):
        if i not in enabled:
            colors[i] = white
    column_of_boxes(x, y, len(colors), 0.2, 0.2, context, colors)


def rain(x, y, context, enabled: Union[bool, List[int]]=True):
    colors = [
        Color(0.0233, 0.210, 0.00630),
        Color(0.0634, 0.430, 0.0301),
        Color(0.0853, 0.770, 0.0231),
        Color(0.645, 0.960, 0.566)
    ]
    if enabled is True:
        enabled = range(len(colors))
    for i in range(len(colors)):
        if i not in enabled:
            colors[i] = white
    column_of_boxes(x, y, len(colors), 0.2, 0.35, context, colors)


def wind(x, y, context, enabled: Union[bool, List[int]]=True):
    colors = [
        Color(0.320, 0.315, 0.0160),
        Color(0.620, 0.611, 0.0806),
        Color(0.820, 0.808, 0.0984),
        Color(0.990, 0.982, 0.515)
    ]
    if enabled is True:
        enabled = range(len(colors))
    for i in range(len(colors)):
        if i not in enabled:
            colors[i] = white
    column_of_boxes(x, y, len(colors), 0.2, 0.35, context, colors)


with open('climates.json', 'r') as f:
    weather_tables = load(f)


WIDTH = 3
HEIGHT = 7
PIXEL_SCALE = 300

surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                             WIDTH*PIXEL_SCALE,
                             HEIGHT*PIXEL_SCALE)
ctx = cairo.Context(surface)
ctx.scale(PIXEL_SCALE, PIXEL_SCALE)

ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.set_source_rgb(1, 1, 1)
ctx.fill()

# Drawing code
grid = Grid(0.7, 1.7, 0.05, 0.05)

climate = 'metzuba'
row = 0
for season_name, season in weather_tables[climate].items():
    column = 0
    for system_name, system in season.items():
        if column == 0:
            left_label = season_name.capitalize()
        else:
            left_label = None
        weather_set(*grid.coords(column, row), ctx, *system, system_name.capitalize(), left_label)
        column += 1
    row += 1


surface.write_to_png(f'{climate}.png')