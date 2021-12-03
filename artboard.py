import math
import random

import drawSvg as draw


class Point:
    # (x, y)
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, p):
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2) ** 0.5

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __neg__(self, other):
        return Point(-self.x, -self.y)

    def __sub__(self, other):
        return self + (-other)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def copy(self):
        return Point(self.x, self.y)

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
        self.line_pixels = {}
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

    def scape_next_pin(self, current, img, min_distance, score_func):
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

            score = score_func(img, self.line_pixels[pair])
            if score > max_score:
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

    def generate_stringscape(self, img, n_strings, fade, min_distance, scoring_method=Scoring.naive):
        # origin top left, (y, x)
        steps = []
        current = 0 # change to darkest point on border?
        steps.append(current)

        ydim = img.shape[0]
        xdim = img.shape[1]
        self.grid = [
            [
                Point(j,i) for j in range(0, xdim)
            ] for i in range(0, ydim)
        ]
        radius = min(xdim, ydim) // 2
        circle_pins = self.calc_img_circle_pins(self.n_pins, Point(xdim / 2, ydim / 2), radius, x_max=xdim-1, x_min=0, y_max=ydim-1, y_min=0, flip_y=True)
        print(circle_pins)
        # move this to __init__?
        for i in range(0, self.n_pins):
            print(f"Circle pin {i}")
            for j in range(i + 1, self.n_pins):
                self.line_pixels[(j, i)] = self.rasterize_line(circle_pins[i], circle_pins[j])

        for i in range(0, n_strings):
            next = self.scape_next_pin(current, img, min_distance, scoring_method)
            self.add_string(next, current)
            print (f"{i}/{n_strings}: {current} -> {next}")
            if next < 0:
                print("No more possible strings!")
                break

            # look into this
            pair = (max(next, current), min(next, current))
            self.reduce_line(img, self.line_pixels[pair], fade)  # is this necessary?

            current = next
        return self

    def render(self, dpi=96, frame='black', background=None):
        # self.printState()
        # TODO: implement polyline
        d = draw.Drawing(self.diameter, self.diameter, origin='center')
        radius = self.diameter / 2.0
        if background is not None:
            d.append(draw.Rectangle(-radius, -radius, self.diameter, self.diameter, fill=background))
        if frame is not None:
            d.append(draw.Circle(0, 0, radius, stroke=frame, stroke_width=5, stroke_opacity=1, fill='none'))
        for i in range(self.n_pins - 1, 0, -1):
            for j in range(0, i):
                for yarn in self.state[i][j]:
                    endPoint = self._get_point(i)
                    startPoint = self._get_point(j)
                    d.append(draw.Line(startPoint.x, startPoint.y, endPoint.x, endPoint.y, stroke_width=yarn.width,
                                       stroke=yarn.color, stroke_opacity=0.4, fill='none'))
        d.setPixelScale(dpi * 0.393701 / 10)
        return d
