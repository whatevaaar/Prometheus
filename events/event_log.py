from collections import deque

import config


class EventLog:
    def __init__(self=8):
        self.events = deque(maxlen=config.MAX_LOGS)

    def add(self, text):
        self.events.appendleft(text)


event_log = EventLog()