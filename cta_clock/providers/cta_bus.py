from datetime import datetime, timedelta
from cta_clock.model import Provider, Line, Time, Direction
from requests_futures.sessions import FuturesSession
from rgbmatrix.graphics import Color

class CTABusProvider(Provider):
    """A provider for the Chicago Transit Authority's rail service. See config.json.default for an example config."""

    def __init__(self, key='', endpoint='http://ctabustracker.com/bustime/api/v2/getpredictions', stop_ids=list()):
        """
        Initialize a CTARailProvider.
        :param key: Your CTA Train Tracker API key.
        :param endpoint: The Train Tracker endpoint.
        """
        super().__init__()
        self.key = key
        self.endpoint = endpoint
        self.stop_ids = stop_ids
        self.update_interval = timedelta(minutes=2)

    def update(self):
        """
        Update all the lines associated with this provider.
        """
        session = FuturesSession()
        print('[cta_bus]\tRequesting updated data for stops', self.stop_ids)
        num_reqs = len(self.stop_ids) // 10 + 1
        for req in range(num_reqs):
            stop_ids = ','.join(self.stop_ids[req * 10:max([(req + 1) * 10, len(self.stop_ids) - 1])])
            session.get("%s?key=%s&stpid=%s&format=json" % (self.endpoint, self.key, stop_ids),
                        background_callback=self._update_bg_cb)

    def _update_bg_cb(self, session, resp):
        try:
            print('[cta_bus]\tResponse from CTA Bus request')
            data = resp.json()['bustime-response']['prd']

            routes = {}
            for prd in data:
                new_time = Time(datetime.strptime(prd['prdtm'],'%Y%m%d %H:%M'),
                                run=int(prd['tatripid']),
                                is_delayed=prd['dly'])
                rt = routes.setdefault(prd['rt'], {})
                dir = rt.setdefault(prd['des'], [])
                dir.append(new_time)

            for line in self.lines:
                dirs = routes.setdefault(line.identifier, {})
                new_dirs = [Direction(dest) for dest in dirs.keys()]

                for dir in new_dirs:
                    dir.times = routes[line.identifier].setdefault(dir.destination, [])

                line.directions = new_dirs

        except Exception:
            import traceback
            print(traceback.format_exc())


def init(config):
    """
    Initialize a CTARailProvider given a config.
    :param config: The object containing the provider's configuration.
    :return: A properly-initialized CTARailProvider, ready to use.
    """
    provider = CTABusProvider(key=config['key'], endpoint=config['endpoint'], stop_ids=config['stop_ids'])
    for line in config['routes'].values():
        new_line = Line(
            identifier=line['identifier'],
            name=line['name'],
            color=Color(line['color'][0], line['color'][1], line['color'][2]),
            directions=[]
        )
        provider.lines.append(new_line)

    provider.update()
    return provider
