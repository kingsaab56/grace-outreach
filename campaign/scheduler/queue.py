from collections import deque


class CampaignQueue:

    def __init__(self):
        self.queue = deque()

    def add(self, email):
        self.queue.append(email)

    def get_next(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def count(self):
        return len(self.queue)

    def clear(self):
        self.queue.clear()