"""
Classes in the ``queues`` plugin namespace represent queues where tasks
are placed as they wait for execution.

Local, in-memory queues are required to be threadsafe.

Remote queues should allow multiple concurrent producers.
"""

from viking.core import Plugin
from Queue import Queue as UpstreamQueue
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

class MemoryQueue(Queue, UpstreamQueue):
    plugin_name = 'memory'

    def __init__(self, uri):
        Queue.__init__(self, uri)
        UpstreamQueue.__init__(self)

    push = UpstreamQueue.put
    pop = UpstreamQueue.get
    count = UpstreamQueue.qsize
