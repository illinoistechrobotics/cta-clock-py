from datetime import datetime, timedelta
from rgbmatrix.graphics import Color


class Provider(object):
    def __init__(self):
        self.last_update = datetime.utcnow()
        self.update_interval = timedelta(minutes=1)
        self.pending_requests = 0

    def update(self):
        raise NotImplementedError()


class RouteProvider(Provider):
    def __init__(self):
        self.lines = []

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

    def next_arrival(self):
        if len(self.times) == 0: return None

        lowest = self.times[0]
        for i, t in enumerate(self.times):
            m = t.minutes()
            if m < 0 or m > 120:
                del self.times[i]
            elif m >= 0 and m < lowest.minutes():
                lowest = t

        return lowest


class Time(object):
    def __init__(self, predicted_arrival, run=0, is_approaching=False, is_scheduled=False, is_fault=False, is_delayed=False):
        assert(isinstance(run, int))
        assert(isinstance(predicted_arrival, datetime))
        assert(isinstance(is_approaching, bool))
        assert(isinstance(is_scheduled, bool))
        assert(isinstance(is_fault, bool))
        assert(isinstance(is_delayed, bool))

        self.run = run
        self.predicted_arrival = predicted_arrival
        self.is_approaching = is_approaching
        self.is_scheduled = is_scheduled
        self.is_fault = is_fault
        self.is_delayed = is_delayed

    def minutes(self):
        return (self.predicted_arrival - datetime.now()).seconds // 60


class MessageProvider(object):
    def __init__(self):
        self.messages = []
        self.last_update = datetime.utcnow()
        self.update_interval = timedelta(minutes=1)
        self.pending_requests = 0

    def update(self):
        raise NotImplementedError()


class Message(object):
    def __init__(self, id, message):
        self.id = id

        if isinstance(message, str):
            self.get_message = lambda: message
        else:
            self.get_message = message


def update_providers(providers):
    for p in providers:
        if p.last_update + p.update_interval < datetime.utcnow():
            p.last_update = datetime.utcnow()
            p.update()