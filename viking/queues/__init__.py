from viking.core import Plugin
import collections

class Queue(Plugin):
    def push(self, item):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError

class MemoryQueue(Queue):
    def __init__(self, *args, **kwargs):
        super(MemoryQueue, self).__init__(*args, **kwargs)

        self.data = collections.deque()

    def push(self, item):
        return self.data.append(item)

    def pop(self):
        return self.data.pop()

    def count(self):
        return len(self.data)
