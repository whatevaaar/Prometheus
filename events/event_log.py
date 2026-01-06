from collections import deque

class EventLog:
    def __init__(self, max_events=8):
        self.events = deque(maxlen=max_events)

    def add(self, text):
        self.events.appendleft(text)
