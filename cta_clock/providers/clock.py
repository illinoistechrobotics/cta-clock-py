from cta_clock.providers.static_messages import MessageProvider, Message
from datetime import datetime

class ClockProvider(MessageProvider):
    def __init__(self):
        super().__init__()
        self.date_format = '%a %b %-d, %Y'
        self.time_format_tick = '%-I:%M %p'
        self.time_format_tock = '%-I %M %p'
        self.messages = [
            Message(0, self.get_date),
            Message(1, self.get_time)
        ]

    def get_date(self):
        return datetime.now().strftime(self.date_format)

    def get_time(self):
        now = datetime.now()
        return now.strftime(self.time_format_tick if now.second % 2 == 0 else self.time_format_tock)

    def update(self):
        pass

def init(config):
    return ClockProvider()
