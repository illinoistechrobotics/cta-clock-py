from datetime import datetime
from rgbmatrix.graphics import Color


class Provider(object):
    def __init__(self):
        self.lines = []
        self.last_update = datetime.utcnow()

    def update(self):
        raise NotImplementedError()


class Line(object):
    def __init__(self, name, directions, color=Color(255, 255, 255), identifier=None):
        assert(isinstance(name, str))
        assert(isinstance(directions, list))
        assert(isinstance(color, Color))
        assert(identifier is None or isinstance(identifier, str))

        self.name = name
        self.color = color
        self.identifier = identifier
        self.directions = directions


class Direction(object):
    def __init__(self, destination):
        assert(isinstance(destination, str))

        self.destination = destination

        self.times = []