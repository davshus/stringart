import math

import drawSvg as draw


class Yarn:
    def __init__(self, width, color):
        self.width = width
        self.color = color


class Artboard:
    def __init__(self, diameter, pins_n, yarn=Yarn(0.5, '#000000')):
        self.diameter = diameter
        self.n_pins = pins_n
        self.current_yarn = yarn
        self.state = [[None] * i for i in range(0, pins_n)]

    def add_string(self, a, b):
        if a == b:
            return False  # TODO: throw?
        self.state[max(a, b)][min(a, b)] = self.current_yarn

    def remove_string(self, a, b):
        if a == b:
            return False  # TODO: throw?
        self.state[max(a, b)][min(a, b)] = False

    def _pin_angle_(self, pin):
        angle_delta = 2 * math.pi / self.n_pins
        return pin * angle_delta + math.pi / 2 # Moves counterclockwise

    def _get_point(self, pin):
        angle = self._pin_angle_(pin)
        radius = self.diameter / 2.0
        return (radius * math.cos(angle), radius * math.sin(angle))

    def _get_length(self, startPin, endPin):
        startPoint = self._get_point(startPin)
        endPoint = self._get_point(endPin)
        return ((startPoint[0] - endPoint[0])**2 + (startPoint[1] - endPoint[1])**2) ** 0.5

    def total_length(self):
        totalLen = 0.0
        for i in range(self.n_pins - 1, 0, -1):
            for j in range(0, i):
                if self.state[i][j] is None:
                    continue
                totalLen += self._get_length(i, j)
        # converting from millimteres to inches
        totalInches = totalLen * 0.0393701
        totalFeet = totalInches / 12.0
        return totalFeet

    def render(self, dpi=96, background=None):
        # TODO: implement polyline
        d = draw.Drawing(self.diameter, self.diameter, origin='center')
        radius = self.diameter / 2.0
        if background is not None:
            d.append(draw.Rectangle(-radius, -radius, self.diameter, self.diameter, fill=background))
        d.append(draw.Circle(0, 0, radius, stroke='black', stroke_width=5, stroke_opacity=1, fill='none'))
        for i in range(self.n_pins - 1, 0, -1):
            for j in range(0, i):
                if self.state[i][j] is None:
                    continue
                yarn = self.state[i][j]
                endPoint = self._get_point(i)
                startPoint = self._get_point(j)
                d.append(draw.Line(startPoint[0], startPoint[1], endPoint[0], endPoint[1], 
                    stroke_width=yarn.width, stroke=yarn.color, stroke_opacity=0.6, fill='none'))
        d.setPixelScale(dpi * 0.393701 / 10)
        return d
