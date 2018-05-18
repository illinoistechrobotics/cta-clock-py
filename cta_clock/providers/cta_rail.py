import requests
from datetime import datetime
from rgbmatrix.graphics import Color
from cta_clock.model import Provider, Line, Direction


class CTARailProvider(Provider):
    def __init__(self, key='', endpoint='http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx'):
        super().__init__()
        self.key = key
        self.endpoint = endpoint

    def update(self):
        for line in self.lines:
            pass

        self.last_update = datetime.utcnow()


class CTARailLine(Line):
    def __init__(self, stop_id, name, directions, color=Color(0, 0, 0), identifier=None):
        super().__init__(name=name, directions=directions, color=color, identifier=identifier)
        self.stop_id = stop_id


def init(config):
    provider = CTARailProvider(key=config['key'], endpoint=config['endpoint'])
    for line in config['lines']:
        new_line = CTARailLine(
            stop_id=int(line['stop_id']),
            name=line['name'],
            directions=[Direction(d) for d in line['directions']],
            color=Color(line['color'][0], line['color'][1], line['color'][2]),
            identifier=line['identifier']
        )
        provider.lines.append(new_line)

    provider.update()
    return provider