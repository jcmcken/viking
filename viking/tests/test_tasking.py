from viking.tasking import TaskManager
from viking.tests import TestCase
from viking.queues import MemoryQueue
from mock import MagicMock

class FakeRemoteQueue(MemoryQueue):
    plugin_name = 'fake-memory'

class TestTaskManager(TestCase):
    def setUp(self):
        super(TestTaskManager, self).setUp()

        self.manager = TaskManager(
          executor='null://', 
          enumerator='list://host1,host2,host3',
        )

        self.manager.pool = MagicMock()

    def test_commands_queued(self):
        self.manager.run(['uptime'])
        # one task for each host
        self.assertEquals(self.manager.pool.add_task.call_count, 3)
        # workers started since we're running on a local queue
        self.assertEquals(self.manager.pool.start.call_count, 1)

    def test_commands_not_queued(self):
        self.manager.run()
        self.assertEquals(self.manager.pool.add_task.call_count, 0)
        # memory queue, but no command -- nothing to do!
        self.assertEquals(self.manager.pool.start.call_count, 0)

    def test_only_queue(self):
        self.manager.work_queue = FakeRemoteQueue('foo://')
        self.manager.run(['uptime'])
        # one task for each host
        self.assertEquals(self.manager.pool.add_task.call_count, 3)
        # no workers started since we're queueing tasks remotely
        self.assertEquals(self.manager.pool.start.call_count, 0)

    def test_only_execute(self):
        self.manager.work_queue = FakeRemoteQueue('foo://')
        self.manager.run()
        # shouldnt queue new tasks, just executing from a pre-built queue
        self.assertEquals(self.manager.pool.add_task.call_count, 0)
        # workers should be workin'
        self.assertEquals(self.manager.pool.start.call_count, 1)
