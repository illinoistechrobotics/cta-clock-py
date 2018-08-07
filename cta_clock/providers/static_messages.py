from cta_clock.model import MessageProvider, Message

from datetime import datetime, timedelta

class StaticMessageProvider(MessageProvider):
    def __init__(self):
        super().__init__()
        self.update_interval = timedelta(seconds=0)
        self.last_update = datetime.max

    def update(self):
        pass

def init(config):
    provider = StaticMessageProvider()
    i = 0
    for m in config['messages']:
        provider.messages.append(Message(i, m))
        i += 1

    return provider