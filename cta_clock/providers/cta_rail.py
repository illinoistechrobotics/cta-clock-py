from requests_futures.sessions import FuturesSession
from datetime import datetime, timedelta
from rgbmatrix.graphics import Color
from cta_clock.model import Provider, Line, Direction, Time


class CTARailProvider(Provider):
    """A provider for the Chicago Transit Authority's rail service. See config.json.default for an example config."""

    def __init__(self, key='', endpoint='http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx'):
        """
        Initialize a CTARailProvider.
        :param key: Your CTA Train Tracker API key.
        :param endpoint: The Train Tracker endpoint.
        """
        super().__init__()
        self.key = key
        self.endpoint = endpoint
        self.update_interval = timedelta(minutes=2)

    def update(self):
        """
        Update all the lines associated with this provider.
        """
        for line in self.lines:
            # let's get some data
            session = FuturesSession()
            print('[cta_rail]\tRequesting updated data for', line.name)
            session.get('%s?key=%s&mapid=%d&outputType=JSON' % (self.endpoint, self.key, line.map_id), background_callback=self._update_bg_cb)

    def _update_bg_cb(self, session, resp):
        try:
            data = resp.json()['ctatt']

            # make sure we have data
            if data['errCd'] != '0':
                print('[cta_rail]\tRequest error:', data['errNm'], ' (%s)' % (data['errCd'],))
                return

            if 'eta' not in data:
                print('[cta_rail]\tNo scheduled services')
                return

            # find our line
            line = None
            for l in self.lines:
                if l.map_id == int(data['eta'][0]['staId']):
                    line = l
                    break

            if not line:
                print('[cta_rail]\tGot a response for map_id %s, which is not registered!' % data['eta'][0]['sta_id'])
                return

            print('[cta_rail]\tResponse from CTA Rail request for', line.name)

            directions = {}

            for eta in data['eta']:
                direction = directions.setdefault(int(eta['destSt']), CTADirection(
                    destination=eta['destNm'],
                    direction_code=int(eta['destSt'])
                ))

                direction.times.append(Time(
                    predicted_arrival=datetime.strptime(eta['arrT'], '%Y-%m-%dT%H:%M:%S'),
                    run=int(eta['rn']),
                    is_approaching=bool(int(eta['isApp'])),
                    is_scheduled=bool(int(eta['isSch'])),
                    is_delayed=bool(int(eta['isDly'])),
                    is_fault=bool(int(eta['isFlt']))
                ))

            line.directions = list(directions.values())
        except Exception:
            import traceback
            print(traceback.format_exc())


class CTARailLine(Line):
    def __init__(self, map_id, name, directions, color=Color(0, 0, 0), identifier=None):
        super().__init__(name=name, directions=directions, color=color, identifier=identifier)
        self.map_id = map_id


class CTADirection(Direction):
    def __init__(self, destination, direction_code):
        super().__init__(destination)
        self.direction_code = direction_code


def init(config):
    """
    Initialize a CTARailProvider given a config.
    :param config: The object containing the provider's configuration.
    :return: A properly-initialized CTARailProvider, ready to use.
    """
    provider = CTARailProvider(key=config['key'], endpoint=config['endpoint'])
    for line in config['lines']:
        new_line = CTARailLine(
            map_id=int(line['map_id']),
            name=line['name'],
            directions=[],
            color=Color(line['color'][0], line['color'][1], line['color'][2]),
            identifier=line['identifier']
        )
        provider.lines.append(new_line)

    provider.update()
    return provider