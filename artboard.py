import math
import random
from collections.abc import MutableMapping
import copy

import drawSvg as draw

def circular_range(start, stop, modulo, step=1): # Only supports step of 1 or -1
    start = start % modulo
    stop = stop % modulo
    index = start
    step = -1 if step < 0 else 1
    while index != stop:
        yield index
        index = (index + step) % modulo

class PinPairMap(MutableMapping):
    def __init__(self, arg=None):
        self._map = {}
        if arg is not None:
            self.update(arg)

    def __getitem__(self, key):
        return self._map[frozenset(key)]

    def __setitem__(self, key, value):
        self._map[frozenset(key)] = value

    def __delitem__(self, key):
        del self._map[frozenset(key)]

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

    def __repr__(self):
        return repr(self._map)

class Point:
    # (x, y)
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, p):
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2) ** 0.5

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __sub__(self, other):
        return self + (-other)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def copy(self):
        return Point(self.x, self.y)

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

class Scoring:
    @staticmethod
    def naive(img, points):
        score = 0
        for p in points:
            c = img[p.y][p.x] & 0xff
            score += 0xff - c
        return score / len(points)


class Yarn:
    def __init__(self, width, color):
        self.width = width
        self.color = color

    def __str__(self):
        return f"({self.width},{self.color})"


class Artboard:
    def __init__(self, diameter, pins_n, yarn=Yarn(0.5, '#000000')):
        self.diameter = diameter
        self.n_pins = pins_n
        self.current_yarn = yarn
        self.n_combinations = self.n_pins ** 2 - self.n_pins / 2.0 * (self.n_pins + 1)
        self.line_pixels = PinPairMap()
        self.state = [[[] for j in range(i)] for i in range(pins_n)]

    def reset(self):
        self.state = [[[] for j in range(i)] for i in range(self.n_pins)]

    def add_string(self, a, b):
        if a == b:
            return False  # TODO: throw?
        self.state[max(a, b)][min(a, b)].append(self.current_yarn)

    def remove_string(self, a, b, index=0):
        if a == b:
            return False  # TODO: throw?
        if len(self.state[max(a, b)][min(a, b)]) > index:
            del asdf[index]

    def _pin_angle_(self, pin):
        angle_delta = 2 * math.pi / self.n_pins
        return pin * angle_delta + math.pi / 2  # Moves counterclockwise

    def _get_point(self, pin):
        angle = self._pin_angle_(pin)
        radius = self.diameter / 2.0
        return Point(radius * math.cos(angle), radius * math.sin(angle))

    def _get_length(self, startPin, endPin):
        startPoint = self._get_point(startPin)
        endPoint = self._get_point(endPin)
        return startPoint.distance(endPoint)

    def total_length(self):
        totalLen = 0.0
        for i in range(self.n_pins - 1, 0, -1):
            for j in range(0, i):
                for yarn in self.state[i][j]:
                    totalLen += self._get_length(i, j)
        # converting from millimteres to inches
        totalInches = totalLen * 0.0393701
        totalFeet = totalInches / 12.0
        return totalFeet

    def printState(self):
        for i in self.state:
            rowStr = ""
            for j in i:
                yarnStr = "["
                for k in j:
                    yarnStr += f"{str(k)} "

                yarnStr = yarnStr[:-1] + "]"
                rowStr += f"{yarnStr}   "
            print(rowStr)

    def scape_next_pin(self, current, img, min_distance):
        max_score = 0
        next = -1
        for i in range(self.n_pins):
            pair = (max(i, current), min(i, current))

            # prevent two consecutive pins with less than minimal distance
            diff = abs(current - i)
            dist = (random.random() * min_distance * 2.0 / 3) + min_distance * 2.0 / 3

            if diff < dist or diff > self.n_pins - dist:
                continue

            # currently doesn't allow more than 1 string
            if len(self.state[pair[0]][pair[1]]) > 0:
                continue

            score = self.scores[pair]
            if i == 0 or score > max_score:
                max_score = score
                next = i

        return next

    def reduce_line(self, img, points, value):
        for p in points:
            c = img[p.y][p.x] & 0xff
            c += value
            if c > 0xff:
                c = 0xff
            img[p.y][p.x] = c

    def rasterize_line(self, a, b):
        points = []
        dx = abs(b.x - a.x)
        dy = -abs(b.y - a.y)
        sx = 1 if a.x < b.x else -1
        sy = 1 if a.y < b.y else -1
        e = dx + dy
        a = a.copy()
        while True:
            points.append(self.grid[a.y][a.x])
            if a.x == b.x and a.y == b.y:
                break
            e2 = 2 * e
            if e2 > dy:
                e += dy
                a.x += sx
            if e2 < dx:
                e += dx
                a.y += sy
        return points

    def calc_img_circle_pins(self, n, center, radius, x_max=None, x_min=None, y_max=None, y_min=None, flip_x = False, flip_y = False):
        pins = []
        for i in range(n):
            x = round(center.x + radius * math.cos(self._pin_angle_(i)))
            y = round(center.y + radius * math.sin(self._pin_angle_(i)))
            if x_max is not None:
                x = min(x_max, x)
            if x_min is not None:
                x = max(x_min, x)
            if y_max is not None:
                y = min(y_max, y)
            if y_min is not None:
                y = max(y_min, y)
            if flip_y and y_max is not None and y_min is not None:
                y = y_min + (y_max - y)
            if flip_x and x_max is not None and x_min is not None:
                x = x_min + (x_max - x)

            pins.append(Point(x, y))
        return pins

    def setup_image(self, img, scoring_method = Scoring.naive):
        ydim = img.shape[0]
        xdim = img.shape[1]
        self.img = img
        self.grid = [
            [
                Point(j, i) for j in range(0, xdim)
            ] for i in range(0, ydim)
        ]
        radius = min(xdim, ydim) // 2
        self.circle_pins = self.calc_img_circle_pins(self.n_pins, Point(xdim / 2, ydim / 2), radius, x_max=xdim-1, x_min=0, y_max=ydim-1, y_min=0, flip_y=True)
        self.scores = PinPairMap()
        for i in range(0, self.n_pins):
            for j in range(i + 1, self.n_pins):
                self.line_pixels[j, i] = self.rasterize_line(self.circle_pins[i], self.circle_pins[j])
                self.scores[j, i] = scoring_method(img, self.line_pixels[j, i])
        print(self.scores)

    def generate_stringscape(self, n_strings, fade, min_distance):
        # PRECONDITION: run setup_image
        # origin top left, (y, x)
        current = 0
        old_scores = copy.deepcopy(self.scores)
        for i in range(0, n_strings):
            next = self.scape_next_pin(current, self.img, min_distance)
            self.add_string(next, current)
            # print (f"{i}/{n_strings}: {current} -> {next}")
            if next < 0:
                print("No more possible strings!")
                break
            string_vec = self.circle_pins[current] - self.circle_pins[next]
            # Reduce the lines based on fade constant and dot product
            for a in circular_range(next + 1, current, self.n_pins):
                for b in circular_range(current + 1, next, self.n_pins):
                    # print(a, b)
                    possible_vec = self.circle_pins[a] - self.circle_pins[b]
                    alignment = (string_vec * possible_vec) / (abs(string_vec) * abs(possible_vec))
                    # print(alignment * fade / 350)
                    self.scores[a, b] = self.scores[a, b] - abs(alignment * fade / len(self.line_pixels[a, b])) # magic number approximately equal to 500 * sqrt(2)

            current = next
        delta_scores = PinPairMap()
        for key in self.scores:
            delta_scores[key] = self.scores[key] - old_scores[key]

        # print(f"OLD: {old_scores}")
        # print(f"NEW: {self.scores}")
        # print(f"DEL: {delta_scores}")
        return self

    def render(self, dpi=96, background=None):
        # self.printState()
        # TODO: implement polyline
        d = draw.Drawing(self.diameter, self.diameter, origin='center')
        radius = self.diameter / 2.0
        if background is not None:
            d.append(draw.Rectangle(-radius, -radius, self.diameter, self.diameter, fill=background))
        d.append(draw.Circle(0, 0, radius, stroke='black', stroke_width=5, stroke_opacity=1, fill='none'))
        for i in range(self.n_pins - 1, 0, -1):
            for j in range(0, i):
                for yarn in self.state[i][j]:
                    endPoint = self._get_point(i)
                    startPoint = self._get_point(j)
                    d.append(draw.Line(startPoint.x, startPoint.y, endPoint.x, endPoint.y, stroke_width=yarn.width,
                                       stroke=yarn.color, stroke_opacity=0.4, fill='none'))
        d.setPixelScale(dpi * 0.393701 / 10)
        return d
