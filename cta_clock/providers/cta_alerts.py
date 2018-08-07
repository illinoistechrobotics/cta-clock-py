from cta_clock.model import MessageProvider, Message
from requests_futures.sessions import FuturesSession
from datetime import datetime, timedelta


class CTAAlertsProvider(MessageProvider):
    def __init__(self, endpoint="http://www.transitchicago.com/api/1.0/alerts.aspx", routes=[]):
        super().__init__()

        self.endpoint = endpoint
        self.routes = routes
        self.update_interval = timedelta(minutes=2)

    def update(self):
        route_list = ','.join(self.routes)

        # build query
        url = self.endpoint + ('?outputType=JSON&activeonly=true&accessibility=false&routeid=%s' % (route_list))
        session = FuturesSession()

        self.pending_requests += 1
        print('[cta_alerts]\tRequesting updated data for routes', self.routes)
        session.get(url, background_callback=self._update_complete)

        self.last_update = datetime.utcnow()

    def _update_complete(self, session, resp):
        self.pending_requests -= 1
        data = resp.json()['CTAAlerts']

        if data['ErrorMessage'] is not None:
            print('[cta_alerts]\tResponse from CTA Alerts API:', data['ErrorMessage'])
            return

        print('[cta_alerts]\tResponse from CTA Alerts API: OK')
        self.messages = []

        for alert in data['Alert']:
            self.messages.append(Message(id=alert['AlertId'], message=alert['ShortDescription']))


def init(config):
    provider = CTAAlertsProvider(endpoint=config['endpoint'], routes=config['routes'])
    provider.update()
    return provider


