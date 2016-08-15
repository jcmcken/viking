from viking.core import Plugin
import collections

class Queue(Plugin):
    plugin_namespace = 'queues'
    abstract_plugin = True

    def push(self, item): # pragma: no cover
        raise NotImplementedError

    def pop(self): # pragma: no cover
        raise NotImplementedError

    def count(self): # pragma: no cover
        raise NotImplementedError

class MemoryQueue(Queue):
    plugin_name = 'memory'

    def __init__(self, *args, **kwargs):
        super(MemoryQueue, self).__init__(*args, **kwargs)

        self.data = collections.deque()

    def push(self, item):
        return self.data.append(item)

    def pop(self):
        return self.data.pop()

    def count(self):
        return len(self.data)
