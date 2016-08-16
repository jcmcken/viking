from viking.queues import MemoryQueue
from viking.tests import TestCase

class TestMemoryQueue(TestCase):
    def setUp(self):
        super(TestMemoryQueue, self).setUp()

        self.queue = MemoryQueue('foo')

    def test_init(self):
        self.assertEquals(self.queue.count(), 0)

    def test_push_pop_same(self):
        self.queue.push('foo')
        self.assertEquals(self.queue.count(), 1)
        self.assertEquals(self.queue.pop(), 'foo')
        self.assertEquals(self.queue.count(), 0)

    def test_push_multi(self):
        self.queue.push('foo')
        self.queue.push('bar')
        self.assertEquals(self.queue.count(), 2)
        items = set([self.queue.pop(), self.queue.pop()])
        self.assertEquals(items, set(['foo', 'bar']))
        self.assertEquals(self.queue.count(), 0)
