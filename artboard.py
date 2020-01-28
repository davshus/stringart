import math

import drawSvg as draw


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
                    d.append(draw.Line(startPoint[0], startPoint[1], endPoint[0], endPoint[1], stroke_width=yarn.width, stroke=yarn.color, stroke_opacity=0.6, fill='none'))
        d.setPixelScale(dpi * 0.393701 / 10)
        return d
