from viking.tests import TestCase
from viking.core import Plugin

class TestExecutors(TestCase):
    def test_print_executor(self):
        executor_cls = Plugin.get_class('executors', 'null://')
        result = executor_cls('host1', ['uptime']).execute()
        self.assertEquals(result['host'], 'host1')
        self.assertEquals(result['command'], ['uptime'])
